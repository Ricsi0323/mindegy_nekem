using System;
using System.Drawing;
using System.Globalization;
using System.Windows.Forms;

namespace FunctionPlotter
{
    public class MainForm : Form
    {
        private TextBox txtExpression;
        private TextBox txtXMin;
        private TextBox txtXMax;
        private TextBox txtSamples;
        private Button btnPlot;
        private PictureBox canvas;
        private Label lblStatus;

        private ExpressionParser parser = new ExpressionParser();

        public MainForm()
        {
            Text = "Függvényrajzoló (C# WinForms)";
            Width = 1000;
            Height = 650;

            var topPanel = new Panel { Dock = DockStyle.Top, Height = 90 };
            Controls.Add(topPanel);

            var lblExpr = new Label { Text = "f(x) =", AutoSize = true, Left = 10, Top = 15 };
            txtExpression = new TextBox { Left = 60, Top = 10, Width = 500, Text = "sin(x)" };

            var lblXMin = new Label { Text = "x min:", AutoSize = true, Left = 580, Top = 15 };
            txtXMin = new TextBox { Left = 630, Top = 10, Width = 80, Text = "-10" };

            var lblXMax = new Label { Text = "x max:", AutoSize = true, Left = 720, Top = 15 };
            txtXMax = new TextBox { Left = 780, Top = 10, Width = 80, Text = "10" };

            var lblSamples = new Label { Text = "minták:", AutoSize = true, Left = 870, Top = 15 };
            txtSamples = new TextBox { Left = 930, Top = 10, Width = 50, Text = "1000" };

            btnPlot = new Button { Text = "Rajzolj", Left = 10, Top = 45, Width = 100, Height = 30 };
            btnPlot.Click += BtnPlot_Click;

            var btnAnalyze = new Button { Text = "Elemzés", Left = 120, Top = 45, Width = 100, Height = 30 };
            btnAnalyze.Click += BtnAnalyze_Click;

            lblStatus = new Label { Text = "", AutoSize = true, Left = 240, Top = 50, ForeColor = Color.DarkSlateGray, MaximumSize = new Size(400, 0) };

            topPanel.Controls.AddRange(new Control[] {
                lblExpr, txtExpression, lblXMin, txtXMin, lblXMax, txtXMax, lblSamples, txtSamples, btnPlot, btnAnalyze, lblStatus
            });

            canvas = new PictureBox { Dock = DockStyle.Fill, BackColor = Color.White };
            canvas.Paint += Canvas_Paint;
            canvas.MouseWheel += Canvas_MouseWheel;
            canvas.MouseDown += Canvas_MouseDown;
            canvas.MouseMove += Canvas_MouseMove;
            canvas.MouseUp += Canvas_MouseUp;
            Controls.Add(canvas);
        }

        private double[] xs, ys;
        private double xMin, xMax;
        private double yMin, yMax;
        private double zoomFactor = 1.0;
        private double panX = 0.0;
        private double panY = 0.0;
        private bool isPanning = false;
        private Point lastMousePos;
        private bool isEasterEgg = false;

        private void BtnPlot_Click(object sender, EventArgs e)
        {
            try
            {
                // Beállítások
                xMin = double.Parse(txtXMin.Text, CultureInfo.InvariantCulture);
                xMax = double.Parse(txtXMax.Text, CultureInfo.InvariantCulture);
                if (xMax <= xMin) throw new ArgumentException("x max legyen nagyobb, mint x min.");
                int n = int.Parse(txtSamples.Text);
                if (n < 2) throw new ArgumentException("A minták száma legyen legalább 2.");

                string expr = txtExpression.Text;
                if (expr == "ml-cr")
                {
                    isEasterEgg = true;
                    lblStatus.Text = "A mi alkalmazásunk!";
                    canvas.Invalidate();
                    return;
                }
                else
                {
                    isEasterEgg = false;
                }

                parser.SetExpression(expr);

                xs = new double[n];
                ys = new double[n];
                double dx = (xMax - xMin) / (n - 1);

                yMin = double.PositiveInfinity;
                yMax = double.NegativeInfinity;

                for (int i = 0; i < n; i++)
                {
                    double x = xMin + i * dx;
                    xs[i] = x;
                    double y = parser.Eval(x);
                    ys[i] = y;

                    if (!double.IsNaN(y) && !double.IsInfinity(y))
                    {
                        if (y < yMin) yMin = y;
                        if (y > yMax) yMax = y;
                    }
                }

                if (double.IsInfinity(yMin) || double.IsInfinity(yMax))
                {
                    yMin = -1;
                    yMax = 1;
                }
                if (Math.Abs(yMax - yMin) < 1e-12)
                {
                    yMax = yMin + 1;
                }

                lblStatus.Text = "Kész.";
                // Reset zoom és pan új rajzoláskor
                zoomFactor = 1.0;
                panX = 0.0;
                panY = 0.0;
                canvas.Invalidate();
            }
            catch (Exception ex)
            {
                lblStatus.Text = "Hiba: " + ex.Message;
            }
        }

        private void BtnAnalyze_Click(object sender, EventArgs e)
        {
            if (xs == null || ys == null)
            {
                lblStatus.Text = "Először rajzolj függvényt!";
                return;
            }

            try
            {
                // Min és Max
                double minY = double.PositiveInfinity;
                double maxY = double.NegativeInfinity;
                foreach (double y in ys)
                {
                    if (!double.IsNaN(y) && !double.IsInfinity(y))
                    {
                        if (y < minY) minY = y;
                        if (y > maxY) maxY = y;
                    }
                }

                // Zérushelyek (közelítőleg ahol keresztezi a tengelyt)
                var zeros = new System.Collections.Generic.List<double>();
                for (int i = 0; i < xs.Length - 1; i++)
                {
                    if ((ys[i] <= 0 && ys[i + 1] >= 0) || (ys[i] >= 0 && ys[i + 1] <= 0))
                    {
                        // Lineáris interpoláció
                        double x1 = xs[i], y1 = ys[i], x2 = xs[i + 1], y2 = ys[i + 1];
                        if (y1 != y2)
                        {
                            double zero = x1 - y1 * (x2 - x1) / (y2 - y1);
                            zeros.Add(Math.Round(zero, 3));
                        }
                    }
                }

                // Konvex/ konkáv check (egyszerű: második derivált előjele)
                string convexity = "Ismeretlen";
                int convexCount = 0, concaveCount = 0;
                for (int i = 1; i < xs.Length - 1; i++)
                {
                    double d1 = ys[i] - ys[i - 1];
                    double d2 = ys[i + 1] - ys[i];
                    double secondDeriv = d2 - d1;
                    if (secondDeriv > 0) convexCount++;
                    else if (secondDeriv < 0) concaveCount++;
                }
                if (convexCount > concaveCount) convexity = "Konvex";
                else if (concaveCount > convexCount) convexity = "Konkáv";

                // Eredmény kiírása
                string result = $"Min: {minY:F3}, Max: {maxY:F3}\n" +
                                $"Értékkészlet: [{minY:F3}, {maxY:F3}]\n" +
                                $"Zérushelyek: {string.Join(", ", zeros)}\n" +
                                $"Konvex/Konkáv: {convexity}";
                lblStatus.Text = result;
            }
            catch (Exception ex)
            {
                lblStatus.Text = "Hiba az elemzésben: " + ex.Message;
            }
        }

        private void Canvas_MouseWheel(object sender, MouseEventArgs e)
        {
            double zoomSpeed = 1.1;
            if (e.Delta > 0)
            {
                zoomFactor *= zoomSpeed;
            }
            else
            {
                zoomFactor /= zoomSpeed;
            }
            // Korlátozzuk a zoomot
            zoomFactor = Math.Max(0.1, Math.Min(10.0, zoomFactor));
            canvas.Invalidate();
        }

        private void Canvas_MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                isPanning = true;
                lastMousePos = e.Location;
            }
        }

        private void Canvas_MouseMove(object sender, MouseEventArgs e)
        {
            if (isPanning)
            {
                double dx = e.X - lastMousePos.X;
                double dy = e.Y - lastMousePos.Y;
                // Pan sebesség
                double panSpeed = (xMax - xMin) / canvas.Width / zoomFactor;
                panX -= dx * panSpeed;
                panY += dy * panSpeed; // y fordított
                lastMousePos = e.Location;
                canvas.Invalidate();
            }
        }

        private void Canvas_MouseUp(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                isPanning = false;
            }
        }

        private void Canvas_Paint(object sender, PaintEventArgs e)
        {
            var g = e.Graphics;
            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

            // Margók
            int left = 60, right = 20, top = 20, bottom = 40;
            int w = canvas.ClientSize.Width - left - right;
            int h = canvas.ClientSize.Height - top - bottom;
            var plotRect = new Rectangle(left, top, w, h);

            // Háttér
            g.FillRectangle(Brushes.White, canvas.ClientRectangle);
            g.FillRectangle(new SolidBrush(Color.FromArgb(248, 248, 248)), plotRect);
            g.DrawRectangle(Pens.Gray, plotRect);

            if (isEasterEgg)
            {
                // Easter Egg: Rajzolj monogramokat
                using var eggFont = new Font("Arial", 48, FontStyle.Bold);
                g.DrawString("ML", eggFont, Brushes.Red, 100, 100);
                g.DrawString("CR", eggFont, Brushes.Blue, canvas.Width - 150, 100);
                return;
            }

            if (xs == null || ys == null) return;

            // Zoom és pan alkalmazása
            double xRange = (xMax - xMin) / zoomFactor;
            double xCenter = (xMin + xMax) / 2 + panX;
            double currentXMin = xCenter - xRange / 2;
            double currentXMax = xCenter + xRange / 2;
            double currentYMin = yMin + panY;
            double currentYMax = yMax + panY;

            // Skálázás
            Func<double, float> mapX = x => (float)(left + (x - currentXMin) * w / (currentXMax - currentXMin));
            Func<double, float> mapY = y => (float)(top + (currentYMax - y) * h / (currentYMax - currentYMin));

            // Tengelyek (x=0, y=0 ha tartományban vannak)
            Pen axisPen = new Pen(Color.Black, 2);
            if (currentXMin <= 0 && 0 <= currentXMax)
            {
                float x0 = mapX(0);
                g.DrawLine(axisPen, x0, top, x0, top + h);
            }
            if (currentYMin <= 0 && 0 <= currentYMax)
            {
                float y0 = mapY(0);
                g.DrawLine(axisPen, left, y0, left + w, y0);
            }

            // Rács és jelölések
            DrawGridAndTicks(g, plotRect, mapX, mapY, currentXMin, currentXMax, currentYMin, currentYMax);

            // Görbe
            Pen curvePen = new Pen(Color.RoyalBlue, 2);
            PointF? prev = null;
            for (int i = 0; i < xs.Length; i++)
            {
                double y = ys[i];
                if (double.IsNaN(y) || double.IsInfinity(y)) { prev = null; continue; }
                var pt = new PointF(mapX(xs[i]), mapY(y));

                // Törés ott, ahol függvény „elszáll” (pl. 1/x a 0 körül)
                if (prev != null)
                {
                    // Ha túl nagy ugrás, megszakítjuk a vonalat
                    if (Math.Abs(pt.Y - prev.Value.Y) > 200)
                        prev = null;
                }

                if (prev != null)
                    g.DrawLine(curvePen, prev.Value, pt);

                prev = pt;
            }

            // Címkék
            using var font = new Font("Segoe UI", 9);
            g.DrawString($"x: [{currentXMin:F3}, {currentXMax:F3}]  y: [{currentYMin:F3}, {currentYMax:F3}]", font, Brushes.Black, left, canvas.ClientSize.Height - bottom + 10);
        }

        private void DrawGridAndTicks(Graphics g, Rectangle plotRect, Func<double, float> mapX, Func<double, float> mapY, double currentXMin, double currentXMax, double currentYMin, double currentYMax)
        {
            // Egyszerű, automatikus osztás: kb. 10 beosztás
            int desiredTicks = 10;
            double xRange = currentXMax - currentXMin;
            double yRange = currentYMax - currentYMin;

            double xStep = NiceStep(xRange / desiredTicks);
            double yStep = NiceStep(yRange / desiredTicks);

            Pen gridPen = new Pen(Color.FromArgb(220, 220, 220));
            using var font = new Font("Segoe UI", 8);
            Brush labelBrush = Brushes.DimGray;

            double xStart = Math.Ceiling(currentXMin / xStep) * xStep;
            for (double x = xStart; x <= currentXMax; x += xStep)
            {
                float px = mapX(x);
                g.DrawLine(gridPen, px, plotRect.Top, px, plotRect.Bottom);
                g.DrawString(x.ToString("G4"), font, labelBrush, px + 2, plotRect.Bottom + 2);
            }

            double yStart = Math.Ceiling(currentYMin / yStep) * yStep;
            for (double y = yStart; y <= currentYMax; y += yStep)
            {
                float py = mapY(y);
                g.DrawLine(gridPen, plotRect.Left, py, plotRect.Right, py);
                g.DrawString(y.ToString("G4"), font, labelBrush, plotRect.Left + 2, py - 14);
            }
        }

        private static double NiceStep(double rough)
        {
            double exp = Math.Floor(Math.Log10(rough));
            double frac = rough / Math.Pow(10, exp);
            double nice;
            if (frac < 1.5) nice = 1;
            else if (frac < 3) nice = 2;
            else if (frac < 7) nice = 5;
            else nice = 10;
            return nice * Math.Pow(10, exp);
        }
    }
}
