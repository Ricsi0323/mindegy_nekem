using System;
using System.Globalization;
using org.mariuszgromada.math.mxparser;

namespace FunctionPlotter
{
    public class ExpressionParser
    {
        static ExpressionParser()
        {
            // Beállítjuk, hogy a trigonometrikus függvények radiánban számítsanak
            mXparser.setRadiansMode();
        }

        private Expression expression;
        private Argument xArgument;

        public void SetExpression(string expr)
        {
            // Magyar függvénynevek cseréje angolra
            expr = expr.Replace("tg(", "tan(");
            expr = expr.Replace("ctg(", "cot(");
            expr = expr.Replace("ln(", "log(");
            // További cserék ha szükséges

            // Létrehozzuk az x argumentumot
            this.xArgument = new Argument("x");
            // Létrehozzuk az mxparser kifejezést az argumentummal
            this.expression = new Expression(expr, xArgument);
        }

        public double Eval(double x)
        {
            try
            {
                // Beállítjuk az x változót
                this.xArgument.setArgumentValue(x);

                // Kiértékeljük
                double result = this.expression.calculate();

                // Ellenőrizzük, hogy érvényes-e az eredmény
                if (double.IsNaN(result) || double.IsInfinity(result))
                {
                    throw new Exception("Érvénytelen eredmény");
                }

                return result;
            }
            catch (Exception ex)
            {
                throw new Exception($"Hiba a kifejezés kiértékelésében: {ex.Message}");
            }
        }
    }
}