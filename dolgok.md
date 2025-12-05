Dolgok ami kellenek a python enviormenthez:
    -pyserial
    -pyautogui vagy keyboard

Hogyan aktiváljuk a python enviormentet:
1. Beírjuk a terminálba ezt:  **python -m venv venv**
    
2. Utána ezt : 
        **.\venv\Scripts\Activate.ps1**
        -Ha erre hibát dob ki akkor a powershell buziskodik
        -a megoldásához edzt kell írni:  
        **Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force**
    
3. Ezek után beírjuk a kettesben lévő parancsot és akkor ilyennek kell meg jelennie a terminálban:
        "**(venv)** PS C:\Users\Agero\Documents\gitcucc\mindegy_nekem-1>" 
    
4. Ha a hármas lépés sikerült akkor már csak a lib-eket kell letölteni
        -Lettöltéd módja pedig: 
        **pip install <lib_név>**