from hashlib import md5
from json import loads
from sys import argv
import os
import requests

TERMINAL = False
"""Variable encargada de activar el uso mediante GUI o terminal"""

FILE_CODE = None

try:
    response_url = requests.get("https://raw.githubusercontent.com/ciberuniverse/server_status/refs/heads/main/server.json", timeout=20)
    data_ = loads(response_url.text)

    DOMAIN_HOST = data_["url"] + "/solve"
    """DOMAIN HOST DEBERIA DE SER UNA VARIBALE DINAMICA QUE TOME SU REFERENCIA DESDE UN HOST Y DESDE AHI SE OBTIENE EL ENLACE
    A DONDE SE ACCEDE
    """

    print(f":: cerTI-srv :: Conexion establecida correctamente con cerTI {data_['version']} ::")

except:
    print(":: cerTI-cli :: Error, no se logro establecer conexion con la nube ::")
    exit(0)

params_ = ["--check", "--solve", "--gui"]
all_dirs = os.listdir(".")

# Esto busca el archivo a escanear dentro de la carpeta de manera semantica
for x in all_dirs:

    if "certificacion_" in x:
        FILE_CODE = x
        """Esta variable se rellena usando el nombre de tu archivo que estas programando"""
        break

if not FILE_CODE:
    print(":: cerTI-cli :: No estas ejecutando el archivo desde la carpeta de certificacion tecnica ::")
    exit(0)

RESP_SOLVE = None
"""Esta variable deberia de contener tu respuesta codificada en str"""

ID = None
"""Esta variable es OBLIGATORIA debe contener tu ID dada en el test tecnico"""

usage_ = """
Uso: 
    :: INTERFAZ GRAFICA ::
    
    >> certi.py --gui
    
    :: LINEA DE COMANDOS ::

    >> certi.py --check|solve -R <tu_archivo_de_respuestas> -ID <ID_Proporcionada_en_cerTI>

Ejemplo:
    certi.py --check -R respuestas.txt -ID PIT:d5098d199d0de6dacc877537cf6aab28
    certi.py --solve -R respuestas.txt -ID PIT:d5098d199d0de6dacc877537cf6aab28

--check: Realiza una validacion de tu respuesta comparando las respuestas esperadas
         localmente para verificar tus respuestas.

--solve: Envia las respuestas a los servidores para su validacion y si corresponde
         entrega del certificado.

:: ADVERTENCIA :: Se realizaran verificaciones constantes por cada ejercicio y certificado
entregado, en caso de que se verifique el intento de engaño, o falta al sistema de verificacion
se realizara una suspencion que quedara a criterio del evaluador.
"""

def check_semantic_v2(permitido: list, denegado: list) -> dict:
    """Se valida que la semantica del codigo este escrita correctamente."""

    def show_sc(elem_: str) -> str:
        """Funcion para ser usada en map, solamente imprime en pantalla"""
        return f"    - {elem_}"

    def map_art(func, message, iterable: list) -> str:
        """Map artesanal para tener mas legibilidad sin for"""    

        for elem in iterable:
            message += f"\n{func(elem)}"

        return message
    
    try:
        with open(FILE_CODE, "r", encoding="UTF-8") as read_code:

            file_ = read_code.read()

            allow = []
            deny = []

            for x in permitido:

                if x not in file_:
                    allow.append(x)

            if allow:

                message = ":: cerTI-cli :: Vas por buen camino, sin embargo no estas cumpliendo con el criterio de evaluacion ::\n:: NO ESTAS USANDO ::"
                return {"status": "error", "message": map_art(show_sc, message, allow)}
            
            for x in denegado:
                
                if x in file_:
                    deny.append(x)
            
            if deny:
                message = ":: cerTI-cli :: Todo bien, pero no puedes utilizar las siguientes sentencias ::\n:: ESTAS USANDO ::"
                return {"status": "error", "message": map_art(show_sc, message, deny)}
            
        return {"status": "ok", "message": ":: cerTI-cli :: Tu codigo si esta poniendo en practica lo que se esta evaluando ::"}
    
    except Exception as err:
        print(f"[ERROR] {err}")
        return {"status": "error", "message": ":: cerTI-cli :: Error al leer el archivo ::"}

def check_semantic(permitido: list, denegado: list) -> bool:
    """Se valida que la semantica del codigo este escrita correctamente."""

    def show_sc(elem_: str) -> None:
        """Funcion para ser usada en map, solamente imprime en pantalla"""
        print(f"    - {elem_}")

    def map_art(func, iterable: list) -> None:
        """Map artesanal para tener mas legibilidad sin for"""    
        for elem in iterable:
            func(elem)
    
    try:
        with open(FILE_CODE, "r", encoding="UTF-8") as read_code:

            file_ = read_code.read()

            allow = []
            deny = []

            for x in permitido:

                if x not in file_:
                    allow.append(x)

            if allow:
                print(f":: Vas por buen camino, sin embargo no estas cumpliendo con el criterio de evaluacion ::\n:: NO ESTAS USANDO ::")
                map_art(show_sc, allow)
                return False
            
            for x in denegado:
                
                if x in file_:
                    deny.append(x)
            
            if deny:
                print(f":: Todo bien, pero no puedes utilizar las siguientes sentencias ::\n:: ESTAS USANDO ::")
                map_art(show_sc, deny)
                return False
            
        return True
    
    except Exception as err:
        print(f"[ERROR] {err}")
        return False

##### ACTUALIZADO CON CHECK SEMANTIC V2
def valid_() -> dict:
    """Valida la semantica del texto con respuestas formato json retornando un status y message"""

    params = {"id": ID}
    """No sacar de aqui no corre"""

    try:
        semantic_ = requests.get(DOMAIN_HOST, params = params)
        
        if "{" not in semantic_.text:
            return {"status": "error", "message": semantic_.text}

        response_  = loads(semantic_.text)

    except Exception as err:
        print(f"[ERROR] {err}")
        return {"status": "error", "message": ":: cerTI-cli :: Error, no logramos establecer conexion con la nube ::"}
        

    denegado = response_["denegado"]
    permitido = response_["permitido"]

    # Se envian los datos para verificar la semantica del archivo
    check_ = check_semantic_v2(permitido, denegado)
    
    return check_

##### ACTUALIZADO CON CHECK SEMANTIC V2
def solve_() -> str:
    """Retorna el mensaje desde el servidor"""

    try:

        # Si es que se esta usando como archivo externo
        # PARA TODOS LOS EXAMENES TECNICOS QUE NO SEAN PYTHON, ESTAN USANDOSE RB PARA EVITAR BUGS DE COMPATIBILIDAD
        if TERMINAL:
            with open(RESP_SOLVE, "rb") as read_:
                hash = md5(read_.read()).hexdigest()

        # Si es que se esta importando como libreria
        else:
            hash = md5(RESP_SOLVE.encode("UTF-8")).hexdigest()

        data = {"key": ID, "solve": hash}


        response_ = requests.post(DOMAIN_HOST, data=data)
        return response_.text

    except Exception as err:
        print(f"[ERROR] {err}")
        return ":: cerTI-cli :: Error, no logramos establecer conexion con la nube ::"

##### ACTUALIZADO CON CHECK SEMANTIC V2
def resolve_tecnical(*args):
    """Funcion encargada de validar desde el propio codigo su validez"""
    global RESP_SOLVE
    
    RESP_SOLVE = str(args)

    if not ID:
        print(":: cerTI-cli :: No has declarado tu ID prueba con certi.ID = '<TU_ID>' ::")
        return
    
    if not FILE_CODE:
        print(":: cerTI-cli :: No has declarado la direccion a tu codigo prueba con certi.FILE_CODE = './tu/archivo.py' ::")
        return

    if len(ID) > 40 or len(ID) < 32:
        print(":: cerTI-cli :: Tu ID no cumple con el formato establecido ::")
        return
    
    response = valid_()

    # Si es que no hay error se retornara lo que el servidor decida
    if response["status"] != "error":
        return solve_()
    
    print(response["message"])
    exit(0)
    
##### ACTUALIZADO CON CHECK SEMANTIC V2
def resolve_tecnical_GUI() -> str:

    response = valid_()

    if response["status"] != "error":
        return solve_()
    
    return response["message"]
    
def main_flask() -> None:
    """Utilizando la GUI de cerTI"""

    import webbrowser
    from flask import Flask, request

    print("""
:: cerTI-cli ::
---------------
>> Estamos usando actualmente la IP 127.0.0.1 en el puerto 5000 para correr esta GUI <<
-------------------------------------------------------------------------------------------
!! Si no se abre correctamente en tu navegador, puede que tengas otro servicio corriendo
en segundo plano. Prueba cerrando el servicio que este ocupando ese puerto y vuelve abrir
cerTI. !! => { http://127.0.0.1:5000 };
""")
    app_ = Flask(__name__)

    NOT_IN = """'";--/*\=%&(){}[]<>$#!?"""

    css_ = """
    <style>
        /* Reset básico y fondo */
        * {
        box-sizing: border-box;
        }

        body {
        margin: 0;
        padding: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
        background: -webkit-linear-gradient(black, rgb(0, 46, 5));
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        }

        a {
        text-decoration: none;
        color: #00ffaa;
        font-weight: 500;
        transition: color 0.3s ease;
        }

        a:hover {
        color: #3f94d5;
        }

        /* Formulario */
        main {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 20px;
        }

        form {
        background-color: rgba(0, 0, 0, 0.65);
        border: 1px solid #00ffaa44;
        border-radius: 12px;
        padding: 25px;
        margin-top: 40px;
        min-width: 300px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        }

        #us {
        font-weight: bold;
        color: #00ffaa;
        }

        input[type="text"]{
        padding: 10px;
        border: none;
        border-radius: 8px;
        outline: none;
        background-color: #111;
        color: #fff;
        }

        input:focus {
        border: 2px solid #00ffaa;
        }

        button{
        
        text-align: center;
        font-weight: bold;

        background-color: #00ffaa;
        color: #000;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        cursor: pointer;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0, 255, 170, 0.3);
        width: 100%;
        }

        button:hover {
        background-color: #00cc88;
        transform: scale(1.05);
        }

        #message_to_show {
            max-width: 200px
            width: 100%
        }

        .eslogan {
            font-family: 'Courier New', Courier, monospace;
            font-size: small;
            color: gray;
            text-align: center;
        }

        /* Responsive */
        @media (max-width: 768px) {
        .nav-left {
            flex-direction: column;
            width: 100%;
            display: none;
            background-color: #000;
            padding: 1rem;
        }

        .nav-left.active {
            display: flex;
        }

        .menu-toggle {
            display: block;
        }

        .certi-navbar {
            flex-direction: column;
            align-items: flex-start;
        }
        }
    </style>
    """

    script_ = """
    <script>
        const NOT_IN = `'";--/*\=%&(){}[]<>$#!?`;
        const COM = `"'´`;


        function is_valid(string_) {
            for (elem of string_) {
                
                if (NOT_IN.includes(elem)) {
                    return false;
                }

            }

            return true;
        }

        // Realiza una validacion de que no existan caracteres especiales var => COM
        document.getElementById("path").addEventListener("input", () => {
            let str_in = document.getElementById("path").value;

            for (x of COM) {
                str_in = str_in.replaceAll(x, "");
                document.getElementById("path").value = str_in;
            }
        })

        document.addEventListener("submit", (e) => {
            e.preventDefault();
            
            const ID = document.getElementById("user_id").value;
            const PATH = document.getElementById("path").value;

            if (ID.length != 36 || !is_valid(ID)) {
                alert(`El ID: ${ID} no es valido.`);
                return;
            }

            if (PATH.length >= 300) {
                alert(`La ruta del archivo: ${PATH} no es valida.`);
                return;
            }

            document.getElementById("bt_send").style.display = "none";

            e.target.submit();

        })
    </script>
    """

    def is_valid(string_):

        for x in NOT_IN:

            if x in string_:
                return False
        
        return True

    @app_.route("/", methods=["GET", "POST"])
    def main():

        global ID, RESP_SOLVE

        def make_(alert_: str = "") -> str:
            """Genera dinamicamente el html de respuesta"""
            nonlocal css_, script_

            main_html = f"""
    <!DOCTYPE html>
    <html lang="es">

    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="shortcut icon" href="https://raw.githubusercontent.com/ciberuniverse/server_status/refs/heads/main/images/logo.ico">
    <title>cerTI - Subida</title>
    {css_}
    </head>

    <body>

    <header>
    </header>

    <main>
        <form method="POST" action="/">
        <center>
        <img src="https://raw.githubusercontent.com/ciberuniverse/server_status/refs/heads/main/images/cerTI_transparent_logo.png" height="200" width="200">
        <p class="eslogan">Certificación libre<br>para desarrolladores libres.<p>
        </center>
        <label for="user_id" id="us">Ingresa tu ID:</label>
        <input type="text" id="user_id" name="user_id" required>

        <label for="path" id="us">Ruta de tu archivo de respuesta:</label>
        <input type="text" id="path" name="path" required>

        <button type="submit" id="bt_send">Verificar</button>
        </form>
    </main>
    {script_}
    {alert_}
    </body>

    </html>
    """
            
            return main_html
        
        if request.method == "GET":
            return make_()

        form = request.form
        
        if len(form["user_id"]) != 36 or not is_valid(form["user_id"]):
            return make_("Error: ID no valida")

        if len(form["path"]) >= 300:
            return make_("Error: Tu direccion de archivo supera el limite estipulado")

        
        ID = form["user_id"]
        RESP_SOLVE = form["path"]

        alert_ = "<script>alert(`"+str(resolve_tecnical_GUI())+"`)</script>"
        return make_(alert_)

    webbrowser.open("http://127.0.0.1:5000")
    app_.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    
    TERMINAL = True

    if len(argv) == 2 and argv[1] == "--gui":
        main_flask(); exit(0)

    if len(argv) != 6 or all(x != argv[1] for x in params_) or "-R" not in argv or "-ID" not in argv:
        print(usage_); exit(0)

    RESP_SOLVE = argv[3]

    ID = argv[5]

    check_ = valid_()
    print(check_["message"])

    if argv[1] == "--solve" and check_["status"] != "error":
        print(solve_())