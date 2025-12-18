@echo off
REM Aktiviraj virtualno okolje
call env\Scripts\activate.bat

REM Preveri, ali je Streamlit nameščen
python -m pip show streamlit >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Streamlit ni nameščen. Namestitev...
    pip install streamlit
)

REM Zaženi Streamlit program
streamlit run app.py