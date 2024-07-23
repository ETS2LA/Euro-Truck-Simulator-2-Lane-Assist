html = """
<html>
    <style>
        body {
            background-color: get_theme();
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        p {
            color: #333;
            font-size: 16px;
            font-family: sans-serif;
        }
    
    @keyframes spinner {
        to {transform: rotate(360deg);}
    }
    
    .spinner:before {
        content: '';
        box-sizing: border-box;
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin-top: 20px;
        margin-left: -10px;
        border-radius: 50%;
        border-top: 2px solid #333;
        border-right: 2px solid transparent;
        animation: spinner .6s linear infinite;
    }

    </style>
    <body class="pywebview-drag-region">
        <div style="flex; justify-content: center; align-items: center;">
            <p>Please wait while we initialize the user interface</p>
            <div class="spinner"></div>
        </div>
    </body>
</html>""""""
<html>
    <style>
        body {
            background-color: get_theme();
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        p {
            color: #333;
            font-size: 16px;
            font-family: sans-serif;
        }
    
    @keyframes spinner {
        to {transform: rotate(360deg);}
    }
    
    .spinner:before {
        content: '';
        box-sizing: border-box;
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin-top: 20px;
        margin-left: -10px;
        border-radius: 50%;
        border-top: 2px solid #333;
        border-right: 2px solid transparent;
        animation: spinner .6s linear infinite;
    }
</html>
"""