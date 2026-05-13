import streamlit as st
import os
from datetime import datetime
from dashboard.load_data import load_data, get_month_labels, get_quality_metrics
from dashboard.utils import apply_filters, render_methodology_expander
from dashboard.tabs import overview, anomalies, zero_consumption, meters, recovery, data_quality, chat

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'micromedicao_tratado.csv')
DATA_FILE = os.path.abspath(DATA_FILE)



LOGO_SVG = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iQ2FtYWRhXzEiIGRhdGEtbmFtZT0iQ2FtYWRhIDEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDEwODAgMTA4MCI+CiAgPGRlZnM+CiAgICA8c3R5bGU+CiAgICAgIC5jbHMtMSB7CiAgICAgICAgZmlsbDogIzE1NTQ3ZTsKICAgICAgfQoKICAgICAgLmNscy0yIHsKICAgICAgICBmaWxsOiAjNGViOWU2OwogICAgICB9CgogICAgICAuY2xzLTMgewogICAgICAgIGZpbGw6ICMzNDZhOTA7CiAgICAgIH0KCiAgICAgIC5jbHMtNCB7CiAgICAgICAgZmlsbDogIzdjY2FlYzsKICAgICAgfQoKICAgICAgLmNscy01IHsKICAgICAgICBmaWxsOiAjMTU1NDdmOwogICAgICB9CgogICAgICAuY2xzLTYgewogICAgICAgIGZpbGw6ICM0MmI0ZTQ7CiAgICAgIH0KCiAgICAgIC5jbHMtNyB7CiAgICAgICAgZmlsbDogIzQzNzU5ODsKICAgICAgfQoKICAgICAgLmNscy04IHsKICAgICAgICBmaWxsOiAjMjNhN2UwOwogICAgICB9CiAgICA8L3N0eWxlPgogIDwvZGVmcz4KICA8Zz4KICAgIDxwYXRoIGNsYXNzPSJjbHMtOCIgZD0iTTE2MC41NCw0MTEuMTFjNC44MiwxLjE2LDkuODksMS4xNiwxNC43MSwwaDEuMzRjMzMuNDgsNC4wNiw2My42LDE2Ljk0LDg2LjcxLDQzLjE4LDE5Ljc5LDIyLjQ2LDMzLjAzLDUxLjc0LDMzLjA5LDgxLjU4LjA0LDE3LjQyLTEyLjcxLDI5LjMyLTI5LjUzLDI5LjY1LTI1LjM5LjUxLTU5LjczLTE2LjAxLTgyLjUyLTI4LjYyLTI1LjgzLTE0LjI5LTc2LjY4LTM4LjA5LTEwNS4zLTM4Ljc3bC0zMi43NC0uNzdjMTguNzktNTEuNDcsNjAuODEtNzkuNzgsMTExLjU3LTg2LjI1aDIuNjdaIi8+CiAgICA8cGF0aCBjbGFzcz0iY2xzLTQiIGQ9Ik0xNzUuMjUsNDExLjExYy00LjAxLDIuMy0xMC43LDIuMy0xNC43MSwwaDE0LjcxWiIvPgogICAgPHBhdGggY2xhc3M9ImNscy01IiBkPSJNMjc4Ljk4LDU4Mi44N2MzLjkzLS45LDcuOTUtMS41MywxMS4xOC0uMi0xOS45OCw1NS42Ny03NC41NCw5MS4wMS0xMzMuMDksODUuNjktNDkuNy00LjUxLTkxLjQtMzYuOTctMTA5LjEtODMuMzgtNi4wMi0xNS43OS0xMC4wMy0zMi4zMi02Ljg1LTQ4LjUyLDUuMTMtMjYuMTEsMzUuNDEtMjMuNiw1NC42LTE3Ljc5LDE5LjE5LDUuODEsMzcuMDgsMTQuMzMsNTQuNzIsMjMuOTksMzEuNjUsMTcuMzQsNzEuNjksMzYuMiwxMDcuNjIsMzkuNTUsNy4yOC42OCwxMy45NCwyLjI3LDIwLjkyLjY2WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMjMxLjY2LDQ0NC41Yy0xLjczLTEuOTEtLjk4LTIuNTgsMS4zNS0xLjI5LDIxLjUzLDEwLjA3LDM3LjA5LDI5LjMzLDQyLjQ5LDUxLjk0LDEuNTksNi42NywyLjU1LDEzLjU1LTEuMSwxOS44OS01LjUyLTIuODItNi4xOC04LjU0LTcuNjctMTMuNjQtNi40Ni0yMi4yMy0xNy41MS00Mi42NC0zNS4wNy01Ni45WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy02IiBkPSJNMjMzLjAxLDQ0My4yMWwtMS4zNSwxLjI5Yy0xLjYzLS44My0zLjI1LTEuNzYtNC40MS0zLjc4LDMuMDgtMS4wMiw0LjAyLDEuNjgsNS43NiwyLjQ5WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy03IiBkPSJNMTA0LjM4LDYyMS45NGMxLjksMS45NiwxLjEsMi43Ny0xLjM5LDEuNDctMjEuMzYtMTAuNzktMzcuODktMjkuMjgtNDMuMDgtNTIuNjMtMS40OC02LjY4LTIuNTEtMTMuNTMsMS4zLTE5LjYzLDQuMjksMi4xNSw1LjQyLDYuMjUsNi40OCwxMC4xLDYuMjksMjIuNzIsMTguMDEsNDcuMDUsMzYuNjksNjAuNjlaIi8+CiAgICA8cGF0aCBjbGFzcz0iY2xzLTMiIGQ9Ik0xMDIuOTgsNjIzLjQyYy41Ny0uMzgsMS4wNC0uODgsMS4zOS0xLjQ3LDEuNDYsMS4wNywyLjk3LDIuMDIsNC4xNSw0LTIuOTIuODEtNC4wNi0xLjQxLTUuNTQtMi41M1oiLz4KICA8L2c+CiAgPGc+CiAgICA8Zz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMzQ3LjcxLDU1NC4yNHYtMy4yMmMyLjcxLTIuODgsMi45NC03LjAxLDUuNDktMTEuNDIsMTEuMDgsMTAuMTUsNDQuODIsMTMuMzgsNDYuMTItMi41MiwxLjM0LTE2LjMzLTE0LjA5LTEzLjk5LTI5LjA3LTE4LTEzLjA0LTMuNDktMjAuODMtMTQuNDYtMTkuNDktMjYuODMsMS44My0xNi45NywxOS45MS0yMi41NiwzNS44My0yMC43Myw4LjQ0Ljk3LDE2LjY1LDIuMDEsMjMuMDQsOC4zNS0yLjQsNC42MS0zLjYsOC4yOC02LjcsMTIuMzYtNy4wNS04LjUyLTMzLjk0LTEyLjMtMzcuMjguMzUtNS41NCwyMC45Nyw0MC43Nyw2LjY2LDQ3LjM5LDM0LjY1LDIuNCwxMC4xNiwxLjQyLDIwLjk5LTcuMywyNy4wMy0xNy41MywxMi4xMi00MC4zOCwxMC4wNi01OC4wMi0uMDJaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTY1NC4xOCw1NjEuMDdjLTIuMSwyLjI1LTEwLjg1LDMuNjYtMTMuNDMuNTNsLTQ0LjQtNTMuODgtLjU1LDU0LjE2Yy00LjUzLDEuNDMtOC4yMiwxLjM1LTEyLjY0LjY1bC4yNS05Mi4xNiw1Ny42NCw2OC44NS4yOC02OC4wN2M0LjU2LS4zNiw4LjI2LS4zOSwxMi44OS4wMmwtLjA0LDg5LjkxWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTUiIGQ9Ik0xMDIyLjAzLDU1NC42NmwtMzguNDQuMjhjLTIuMTcsMS4zNy0yLjU3LDUuMjMtNC4wOCw3LjQ1LTQuNzUuNi04Ljk4LjY2LTE0LjU2LS4wOWwzNy42Ny05MS40NCwzNy4xMyw4OS45NmMtNC41MSwyLjY2LTkuMywyLjMxLTE0LjExLDEuNTFsLTMuNjMtNy42OFpNMTAxNy44Niw1NDIuMjhsLTE1LjcxLTM4LjI4LTE0LjYzLDM5LjM1YzEwLjk1LS42NCwyMC40MiwxLjQyLDMwLjM0LTEuMDZaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTUxNi44Myw1NTUuMDJsLTM5LjgzLS43MS0zLjY2LDcuOTdjLTUuMDIuMjgtOS4yNy41Mi0xNC42NC0uMTRsMzcuODktOTEuMDIsMzcuMjIsODkuODFjLTQuNDgsMi41My04LjY5LDEuOC0xMy4xMiwxLjA1LTIuMTUtLjE4LTIuMzEtNS43My0zLjg2LTYuOTVaTTQ4MS40Miw1NDIuODhsMzAuNzctLjExLTE2LTM5LjgzYy0zLjIyLDcuMDUtMi44NCwxMy4zLTcuMzYsMTguNTUtMS40NSw3LjYxLTUuMjksMTMuNDQtNy40LDIxLjM5WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05MDIuMzEsNDcyLjY4YzEuNjMtMy44MSwxMC41NC0xLjU4LDE0Ljc2LS4zNGwtMzcuNzgsOTAuODgtMzYuOTQtOTEuMDZjNC4zOC0yLjE1LDkuMzItMS4zMSwxNC41My0uMTZsMjIuNDIsNTQuMzIsMjMuMDEtNTMuNjVaIi8+CiAgICAgIDxnPgogICAgICAgIDxwYXRoIGNsYXNzPSJjbHMtOCIgZD0iTTc3OC41Nyw1MjMuODFjMS44OC0xNy42NS00LjgzLTMxLjg2LTIwLjEtMzcuMDgtMTQuNDMtNC45My0zMC40NC44My0zNy41MywxNi01LjIxLjMzLTkuNjMtMS41LTE1LjQ2LTEuNzIsNy4wMy0xOS42MSwyNy4wMS0zMi4xMiw0Ny40Ni0yOS45MywzNC42NywzLjcyLDQ2Ljk4LDQyLjkxLDM4LjQzLDUyLjUxLTIuMjYsMi41NC0xMi41MSwzLjk1LTEyLjgxLjIyWiIvPgogICAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTc3Ni40LDUzMC43M2M1LjYuOTEsOS43NCwxLjc0LDE1LjMsMS41Ny01LjczLDE2LjI2LTE5LjYxLDI2LjkyLTM0LjY4LDI5Ljc4LTE3LjU1LDMuMzMtMzQuMjctMi44Ny00NC45Mi0xNi44Ni00Ljk3LTYuNTMtMTQuNTktMjcuNzQtNi40NS0zNS4wNiwzLjAzLTIuNzIsNi42OC0yLjc5LDEzLjAzLTEuNzktNS42NiwxOC40NCw3LjI2LDM4Ljc5LDI3Ljg5LDQwLjk4LDEyLjg0LDEuMzYsMjMuNzMtNi45MywyOS44My0xOC42MloiLz4KICAgICAgPC9nPgogICAgPC9nPgogICAgPGc+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTM1MC4wNSw2MDIuMDhjLjk0LjU4LDIuMzIsMS4wNywzLjc4LDEuMDcsMi4xNSwwLDMuNDEtMS4xNCwzLjQxLTIuNzgsMC0xLjUyLS44Ny0yLjQtMy4wNy0zLjI0LTIuNjYtLjk0LTQuMzEtMi4zMi00LjMxLTQuNjIsMC0yLjU0LDIuMTEtNC40Myw1LjI4LTQuNDMsMS42NywwLDIuODguMzksMy42MS44bC0uNTgsMS43MmMtLjUzLS4yOS0xLjYyLS43Ny0zLjEtLjc3LTIuMjMsMC0zLjA3LDEuMzMtMy4wNywyLjQ1LDAsMS41Mi45OSwyLjI4LDMuMjQsMy4xNSwyLjc2LDEuMDcsNC4xNiwyLjQsNC4xNiw0Ljc5LDAsMi41Mi0xLjg2LDQuNy01LjcxLDQuNy0xLjU3LDAtMy4yOS0uNDYtNC4xNi0xLjA0bC41My0xLjc3WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0zODguNzMsNTk2LjMyYzAsNS42Mi0zLjQxLDguNTktNy41OCw4LjU5cy03LjM0LTMuMzQtNy4zNC04LjI4YzAtNS4xOCwzLjIyLTguNTcsNy41OC04LjU3czcuMzQsMy40MSw3LjM0LDguMjZaTTM3Ni4wNyw1OTYuNTljMCwzLjQ5LDEuODksNi42MSw1LjIxLDYuNjFzNS4yMy0zLjA3LDUuMjMtNi43OGMwLTMuMjQtMS42OS02LjYzLTUuMjEtNi42M3MtNS4yMywzLjIyLTUuMjMsNi44WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik00MDMuOTgsNTg4LjMzaDIuMTF2MTQuNTVoNi45N3YxLjc3aC05LjA4di0xNi4zMloiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDI5LjE1LDU4OC4zM3Y5LjY2YzAsMy42NiwxLjYyLDUuMiwzLjgsNS4yLDIuNDIsMCwzLjk3LTEuNiwzLjk3LTUuMnYtOS42NmgyLjEzdjkuNTFjMCw1LjAxLTIuNjQsNy4wNy02LjE3LDcuMDctMy4zNCwwLTUuODYtMS45MS01Ljg2LTYuOTd2LTkuNjFoMi4xM1oiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDY2LjYyLDYwNC4xMmMtLjc3LjM5LTIuMy43Ny00LjI4Ljc3bC0uNTYuOTdjLjkuMTcsMS42OS44MiwxLjY5LDEuODIsMCwxLjQtMS4yMywxLjk2LTIuNDksMS45Ni0uNjMsMC0xLjMxLS4xNy0xLjcyLS40MWwuMzQtMS4wOWMuMzYuMTkuODIuMzIsMS4zNi4zMnMxLjAyLS4yMiwxLjAyLS43M2MwLS42NS0uNzUtLjkyLTEuODktMS4wNGwxLjAyLTEuODZjLTMuOTktLjQ4LTYuODUtMy4zMi02Ljg1LTguMTgsMC01LjExLDMuNDYtOC41Nyw4LjUyLTguNTcsMi4wMywwLDMuMzIuNDQsMy44Ny43M2wtLjUxLDEuNzJjLS44LS4zOS0xLjk0LS42OC0zLjI5LS42OC0zLjgzLDAtNi4zNywyLjQ1LTYuMzcsNi43MywwLDMuOTksMi4zLDYuNTYsNi4yNyw2LjU2LDEuMjgsMCwyLjU5LS4yNywzLjQ0LS42OGwuNDQsMS42N1oiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDk1LjIxLDU5Ni4zMmMwLDUuNjItMy40MSw4LjU5LTcuNTgsOC41OXMtNy4zNC0zLjM0LTcuMzQtOC4yOGMwLTUuMTgsMy4yMi04LjU3LDcuNTgtOC41N3M3LjM0LDMuNDEsNy4zNCw4LjI2Wk00ODIuNTUsNTk2LjU5YzAsMy40OSwxLjg5LDYuNjEsNS4yMSw2LjYxczUuMjMtMy4wNyw1LjIzLTYuNzhjMC0zLjI0LTEuNjktNi42My01LjIxLTYuNjNzLTUuMjMsMy4yMi01LjIzLDYuOFpNNDg0Ljc1LDU4Ny4yOWMtLjA1LTEuNDguNTgtMi40NywxLjY1LTIuNDcuNTMsMCwuOTIuMTksMS40My40OC4zOS4yMi43Ny40NCwxLjE2LjQ0LjM2LDAsLjU4LS4xNy42NS0uOTRoMS4xMWMuMDIsMS41Mi0uNTEsMi4zNS0xLjYyLDIuMzUtLjUxLDAtLjk0LS4xOS0xLjQ4LS40Ni0uNDYtLjI0LS44LS40Ni0xLjE0LS40Ni0uMzksMC0uNTguNDEtLjYzLDEuMDdoLTEuMTRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTUxOC45MSw1OTdoLTYuMzR2NS44OGg3LjA3djEuNzdoLTkuMTh2LTE2LjMyaDguODF2MS43N2gtNi43MXY1LjE2aDYuMzR2MS43NFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNTM0LjU5LDYwMi4wOGMuOTQuNTgsMi4zMiwxLjA3LDMuNzgsMS4wNywyLjE1LDAsMy40MS0xLjE0LDMuNDEtMi43OCwwLTEuNTItLjg3LTIuNC0zLjA3LTMuMjQtMi42Ni0uOTQtNC4zMS0yLjMyLTQuMzEtNC42MiwwLTIuNTQsMi4xMS00LjQzLDUuMjgtNC40MywxLjY3LDAsMi44OC4zOSwzLjYxLjhsLS41OCwxLjcyYy0uNTMtLjI5LTEuNjItLjc3LTMuMS0uNzctMi4yMywwLTMuMDcsMS4zMy0zLjA3LDIuNDUsMCwxLjUyLjk5LDIuMjgsMy4yNCwzLjE1LDIuNzYsMS4wNyw0LjE2LDIuNCw0LjE2LDQuNzksMCwyLjUyLTEuODYsNC43LTUuNzEsNC43LTEuNTcsMC0zLjI5LS40Ni00LjE2LTEuMDRsLjUzLTEuNzdaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTU3Ni45Nyw1ODguNTJjMS4wMi0uMTcsMi4zNS0uMzEsNC4wNC0uMzEsMi4wOCwwLDMuNjEuNDgsNC41OCwxLjM2LjkuNzcsMS40MywxLjk2LDEuNDMsMy40MXMtLjQ0LDIuNjQtMS4yNiwzLjQ5Yy0xLjExLDEuMTktMi45MywxLjc5LTQuOTksMS43OS0uNjMsMC0xLjIxLS4wMi0xLjY5LS4xNXY2LjU0aC0yLjExdi0xNi4xMlpNNTc5LjA4LDU5Ni4zOWMuNDYuMTIsMS4wNC4xNywxLjc0LjE3LDIuNTQsMCw0LjA5LTEuMjQsNC4wOS0zLjQ5cy0xLjUyLTMuMi0zLjg1LTMuMmMtLjkyLDAtMS42Mi4wNy0xLjk5LjE3djYuMzRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTYwMi45Nyw1OTkuNTJsLTEuNjksNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk02MDguMzIsNTk3Ljg3bC0xLjYtNC43Yy0uMzYtMS4wNy0uNjEtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTYyNy42Niw1ODguNTVjMS4wNy0uMjIsMi41OS0uMzQsNC4wNC0uMzQsMi4yNSwwLDMuNy40MSw0LjcyLDEuMzMuODIuNzMsMS4yOCwxLjg0LDEuMjgsMy4xLDAsMi4xNS0xLjM2LDMuNTgtMy4wNyw0LjE2di4wN2MxLjI2LjQ0LDIuMDEsMS42LDIuNCwzLjI5LjUzLDIuMjguOTIsMy44NSwxLjI2LDQuNDhoLTIuMThjLS4yNy0uNDYtLjYzLTEuODYtMS4wOS0zLjktLjQ4LTIuMjUtMS4zNi0zLjEtMy4yNy0zLjE3aC0xLjk5djcuMDdoLTIuMTF2LTE2LjFaTTYyOS43Nyw1OTUuOThoMi4xNWMyLjI1LDAsMy42OC0xLjI0LDMuNjgtMy4xLDAtMi4xMS0xLjUyLTMuMDMtMy43NS0zLjA1LTEuMDIsMC0xLjc0LjEtMi4wOC4xOXY1Ljk2WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik02NTUuOTYsNTk5LjUybC0xLjY5LDUuMTNoLTIuMThsNS41NC0xNi4zMmgyLjU0bDUuNTcsMTYuMzJoLTIuMjVsLTEuNzQtNS4xM2gtNS43OVpNNjYxLjMxLDU5Ny44N2wtMS42LTQuN2MtLjM2LTEuMDctLjYtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTcxMC43MSw2MDMuOTJjLS45NC4zNC0yLjgxLjktNS4wMS45LTIuNDcsMC00LjUtLjYzLTYuMS0yLjE1LTEuNC0xLjM2LTIuMjgtMy41My0yLjI4LTYuMDguMDItNC44NywzLjM3LTguNDIsOC44NC04LjQyLDEuODksMCwzLjM2LjQxLDQuMDcuNzVsLS41MSwxLjcyYy0uODctLjM5LTEuOTYtLjctMy42MS0uNy0zLjk3LDAtNi41NiwyLjQ3LTYuNTYsNi41NnMyLjQ5LDYuNTgsNi4yOSw2LjU4YzEuMzgsMCwyLjMyLS4xOSwyLjgxLS40NHYtNC44N2gtMy4zMnYtMS42OWg1LjM3djcuODRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTczNC44OSw1OTdoLTYuMzR2NS44OGg3LjA3djEuNzdoLTkuMTd2LTE2LjMyaDguODF2MS43N2gtNi43MXY1LjE2aDYuMzR2MS43NFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNzUwLjU3LDYwMi4wOGMuOTQuNTgsMi4zMiwxLjA3LDMuNzgsMS4wNywyLjE1LDAsMy40MS0xLjE0LDMuNDEtMi43OCwwLTEuNTItLjg3LTIuNC0zLjA3LTMuMjQtMi42Ni0uOTQtNC4zMS0yLjMyLTQuMzEtNC42MiwwLTIuNTQsMi4xMS00LjQzLDUuMjgtNC40MywxLjY3LDAsMi44OC4zOSwzLjYxLjhsLS41OCwxLjcyYy0uNTMtLjI5LTEuNjItLjc3LTMuMS0uNzctMi4yMywwLTMuMDcsMS4zMy0zLjA3LDIuNDUsMCwxLjUyLjk5LDIuMjgsMy4yNCwzLjE1LDIuNzYsMS4wNyw0LjE2LDIuNCw0LjE2LDQuNzksMCwyLjUyLTEuODYsNC43LTUuNzEsNC43LTEuNTcsMC0zLjI5LS40Ni00LjE2LTEuMDRsLjUzLTEuNzdaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTc3OC40MSw1OTAuMTJoLTQuOTZ2LTEuNzloMTIuMDh2MS43OWgtNC45OXYxNC41M2gtMi4xM3YtMTQuNTNaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTgwMC42OCw1OTkuNTJsLTEuNjksNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk04MDAuNjgsNTg3LjM0Yy0uMDItMS40OC42MS0yLjQ3LDEuNjUtMi40Ny41MywwLC45NC4yMiwxLjQ1LjQ4LjM5LjIyLjc3LjQ0LDEuMTQuNDQuMzksMCwuNi0uMTcuNjUtLjk0aDEuMTRjLjAyLDEuNTMtLjUxLDIuMzUtMS42NSwyLjM1LS41MSwwLS45NC0uMTktMS40OC0uNDYtLjQ2LS4yNC0uNzctLjQ2LTEuMTQtLjQ2LS4zOSwwLS41Ni40MS0uNjMsMS4wN2gtMS4xNFpNODA2LjAzLDU5Ny44N2wtMS42LTQuN2MtLjM2LTEuMDctLjYtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTgzOC45NSw1OTYuMzJjMCw1LjYyLTMuNDEsOC41OS03LjU4LDguNTlzLTcuMzQtMy4zNC03LjM0LTguMjhjMC01LjE4LDMuMjItOC41Nyw3LjU4LTguNTdzNy4zNCwzLjQxLDcuMzQsOC4yNlpNODI2LjI5LDU5Ni41OWMwLDMuNDksMS44OSw2LjYxLDUuMiw2LjYxczUuMjMtMy4wNyw1LjIzLTYuNzhjMC0zLjI0LTEuNjktNi42My01LjItNi42M3MtNS4yMywzLjIyLTUuMjMsNi44WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik04NzEuODQsNTg4LjU1YzEuMjgtLjE5LDIuODEtLjM0LDQuNDgtLjM0LDMuMDMsMCw1LjE4LjcsNi42MSwyLjAzLDEuNDUsMS4zMywyLjMsMy4yMiwyLjMsNS44NnMtLjgyLDQuODQtMi4zNSw2LjM0Yy0xLjUyLDEuNTItNC4wNCwyLjM1LTcuMjEsMi4zNS0xLjUsMC0yLjc2LS4wNy0zLjgzLS4xOXYtMTYuMDVaTTg3My45NSw2MDIuOThjLjUzLjEsMS4zMS4xMiwyLjEzLjEyLDQuNSwwLDYuOTUtMi41Miw2Ljk1LTYuOTIuMDItMy44NS0yLjE1LTYuMjktNi42MS02LjI5LTEuMDksMC0xLjkxLjEtMi40Ny4yMnYxMi44OFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNOTAyLjc4LDU5OS41MmwtMS42OSw1LjEzaC0yLjE4bDUuNTQtMTYuMzJoMi41NGw1LjU3LDE2LjMyaC0yLjI1bC0xLjc0LTUuMTNoLTUuNzlaTTkwOC4xMyw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42LTIuMDMtLjg1LTIuOThoLS4wNWMtLjI0Ljk3LS41MSwxLjk2LS44MiwyLjk1bC0xLjYsNC43Mmg0LjkxWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05NDcuNzUsNTk5LjUybC0xLjcsNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk05NTMuMSw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42MS0yLjAzLS44NS0yLjk4aC0uMDVjLS4yNC45Ny0uNTEsMS45Ni0uODIsMi45NWwtMS42LDQuNzJoNC45MVpNOTU0LjI2LDU4NC42M2wtMy4wNywyLjgzaC0xLjc0bDIuMjUtMi44M2gyLjU3WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05ODQuNSw2MDMuOTJjLS45NC4zNC0yLjgxLjktNS4wMS45LTIuNDcsMC00LjUtLjYzLTYuMS0yLjE1LTEuNC0xLjM2LTIuMjgtMy41My0yLjI4LTYuMDguMDItNC44NywzLjM3LTguNDIsOC44NC04LjQyLDEuODksMCwzLjM3LjQxLDQuMDcuNzVsLS41MSwxLjcyYy0uODctLjM5LTEuOTYtLjctMy42MS0uNy0zLjk3LDAtNi41NiwyLjQ3LTYuNTYsNi41NnMyLjQ5LDYuNTgsNi4yOSw2LjU4YzEuMzgsMCwyLjMyLS4xOSwyLjgxLS40NHYtNC44N2gtMy4zMnYtMS42OWg1LjM3djcuODRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTEwMDIuMzMsNTg4LjMzdjkuNjZjMCwzLjY2LDEuNjIsNS4yLDMuOCw1LjIsMi40MiwwLDMuOTctMS42LDMuOTctNS4ydi05LjY2aDIuMTN2OS41MWMwLDUuMDEtMi42NCw3LjA3LTYuMTcsNy4wNy0zLjM0LDAtNS44Ni0xLjkxLTUuODYtNi45N3YtOS42MWgyLjEzWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMDMwLjIyLDU5OS41MmwtMS43LDUuMTNoLTIuMThsNS41NC0xNi4zMmgyLjU0bDUuNTcsMTYuMzJoLTIuMjVsLTEuNzQtNS4xM2gtNS43OVpNMTAzNS41Nyw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42MS0yLjAzLS44NS0yLjk4aC0uMDVjLS4yNC45Ny0uNTEsMS45Ni0uODIsMi45NWwtMS42LDQuNzJoNC45MVoiLz4KICAgIDwvZz4KICA8L2c+Cjwvc3ZnPg=="



def render_header():
    st.html('''
    <style>
        .stApp { background: #0E1117; }
        .page-header {
            display: flex !important;
            align-items: center !important;
            gap: 28px !important;
            padding: 16px 0 12px 0 !important;
        }
        .page-header-img {
            height: 110px !important;
            width: auto !important;
            flex-shrink: 0 !important;
        }
        .page-header-text {
            display: flex !important;
            flex-direction: column !important;
            gap: 6px !important;
            justify-content: center !important;
        }
        .page-headline {
            font-size: 2.6rem !important;
            font-weight: 800 !important;
            color: #2980B9 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.1 !important;
            font-family: inherit !important;
        }
        .page-subtitle {
            font-size: 1.15rem !important;
            color: #9BA0A6 !important;
            margin: 0 !important;
            font-weight: 400 !important;
            font-family: inherit !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4 {
            color: var(--texto-principal);
        }
        div[data-testid="stMetric"] {
            border-left: 4px solid var(--cor-agua);
            padding: 12px 16px;
            background: var(--bg-card);
            border-radius: 6px;
            color: var(--texto-principal);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--texto-principal) !important;
        }
        div[data-testid="stMetric"].metric-critico { border-left-color: var(--cor-critico); }
        div[data-testid="stMetric"].metric-alerta { border-left-color: var(--cor-alerta); }
        div[data-testid="stMetric"].metric-sucesso { border-left-color: var(--cor-sucesso); }
        .sidebar-section {
            background: var(--bg-sidebar-section);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            border: 1px solid var(--borda);
            color: var(--texto-principal);
        }
        .sidebar-section-title {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--texto-secundario);
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .info-badge {
            display: inline-block;
            background: var(--cor-agua);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .info-badge.alerta { background: var(--cor-alerta); }
        .info-badge.critico { background: var(--cor-critico); }
        .info-badge.sucesso { background: var(--cor-sucesso); }
        .divider-custom {
            border: none;
            border-top: 1px solid var(--borda);
            margin: 16px 0;
        }
        button[data-testid="stTab"] { color: var(--texto-secundario); }
        button[data-testid="stTab"]:active,
        button[data-testid="stTab"][aria-selected="true"] {
            color: var(--cor-agua);
        }
        .stDataFrame tbody { color: var(--texto-principal); }
        .stDataFrame thead th { color: var(--texto-secundario); }
        .streamlit-expander { background: var(--bg-card); border: 1px solid var(--borda); border-radius: 6px; }
        h1, h2, h3, h4, p, span { color: var(--texto-principal); }
        .stCaption, [data-testid="stCaption"] {
            color: var(--texto-secundario) !important;
        }
        .filter-count {
            color: var(--texto-secundario);
            font-size: 0.85rem;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] { margin: 3px 0; }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
            display: flex;
            align-items: center;
            background: var(--bg-sidebar-section);
            border: 1px solid var(--borda);
            border-radius: 6px;
            padding: 8px 12px;
            margin: 0;
            font-size: 0.82rem;
            color: var(--texto-secundario);
            cursor: pointer;
            transition: all 0.15s ease;
            gap: 10px;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover {
            border-color: var(--cor-agua);
            color: var(--texto-principal);
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:first-child {
            flex-shrink: 0;
            display: flex;
            align-items: center;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:last-child {
            flex: 1;
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
        }
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] input:checked + div:last-child,
        section[data-testid="stSidebar"] [data-testid="stCheckbox"] label:has(input:checked) {
            background: var(--cor-agua);
            border-color: var(--cor-agua);
            color: white;
        }
    </style>
    <script>
    var link = document.createElement('link');
    link.rel = 'icon';
    link.type = 'image/svg+xml';
    link.href = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iQ2FtYWRhXzEiIGRhdGEtbmFtZT0iQ2FtYWRhIDEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDEwODAgMTA4MCI+CiAgPGRlZnM+CiAgICA8c3R5bGU+CiAgICAgIC5jbHMtMSB7CiAgICAgICAgZmlsbDogIzE1NTQ3ZTsKICAgICAgfQoKICAgICAgLmNscy0yIHsKICAgICAgICBmaWxsOiAjNGViOWU2OwogICAgICB9CgogICAgICAuY2xzLTMgewogICAgICAgIGZpbGw6ICMzNDZhOTA7CiAgICAgIH0KCiAgICAgIC5jbHMtNCB7CiAgICAgICAgZmlsbDogIzdjY2FlYzsKICAgICAgfQoKICAgICAgLmNscy01IHsKICAgICAgICBmaWxsOiAjMTU1NDdmOwogICAgICB9CgogICAgICAuY2xzLTYgewogICAgICAgIGZpbGw6ICM0MmI0ZTQ7CiAgICAgIH0KCiAgICAgIC5jbHMtNyB7CiAgICAgICAgZmlsbDogIzQzNzU5ODsKICAgICAgfQoKICAgICAgLmNscy04IHsKICAgICAgICBmaWxsOiAjMjNhN2UwOwogICAgICB9CiAgICA8L3N0eWxlPgogIDwvZGVmcz4KICA8Zz4KICAgIDxwYXRoIGNsYXNzPSJjbHMtOCIgZD0iTTE2MC41NCw0MTEuMTFjNC44MiwxLjE2LDkuODksMS4xNiwxNC43MSwwaDEuMzRjMzMuNDgsNC4wNiw2My42LDE2Ljk0LDg2LjcxLDQzLjE4LDE5Ljc5LDIyLjQ2LDMzLjAzLDUxLjc0LDMzLjA5LDgxLjU4LjA0LDE3LjQyLTEyLjcxLDI5LjMyLTI5LjUzLDI5LjY1LTI1LjM5LjUxLTU5LjczLTE2LjAxLTgyLjUyLTI4LjYyLTI1LjgzLTE0LjI5LTc2LjY4LTM4LjA5LTEwNS4zLTM4Ljc3bC0zMi43NC0uNzdjMTguNzktNTEuNDcsNjAuODEtNzkuNzgsMTExLjU3LTg2LjI1aDIuNjdaIi8+CiAgICA8cGF0aCBjbGFzcz0iY2xzLTQiIGQ9Ik0xNzUuMjUsNDExLjExYy00LjAxLDIuMy0xMC43LDIuMy0xNC43MSwwaDE0LjcxWiIvPgogICAgPHBhdGggY2xhc3M9ImNscy01IiBkPSJNMjc4Ljk4LDU4Mi44N2MzLjkzLS45LDcuOTUtMS41MywxMS4xOC0uMi0xOS45OCw1NS42Ny03NC41NCw5MS4wMS0xMzMuMDksODUuNjktNDkuNy00LjUxLTkxLjQtMzYuOTctMTA5LjEtODMuMzgtNi4wMi0xNS43OS0xMC4wMy0zMi4zMi02Ljg1LTQ4LjUyLDUuMTMtMjYuMTEsMzUuNDEtMjMuNiw1NC42LTE3Ljc5LDE5LjE5LDUuODEsMzcuMDgsMTQuMzMsNTQuNzIsMjMuOTksMzEuNjUsMTcuMzQsNzEuNjksMzYuMiwxMDcuNjIsMzkuNTUsNy4yOC42OCwxMy45NCwyLjI3LDIwLjkyLjY2WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMjMxLjY2LDQ0NC41Yy0xLjczLTEuOTEtLjk4LTIuNTgsMS4zNS0xLjI5LDIxLjUzLDEwLjA3LDM3LjA5LDI5LjMzLDQyLjQ5LDUxLjk0LDEuNTksNi42NywyLjU1LDEzLjU1LTEuMSwxOS44OS01LjUyLTIuODItNi4xOC04LjU0LTcuNjctMTMuNjQtNi40Ni0yMi4yMy0xNy41MS00Mi42NC0zNS4wNy01Ni45WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy02IiBkPSJNMjMzLjAxLDQ0My4yMWwtMS4zNSwxLjI5Yy0xLjYzLS44My0zLjI1LTEuNzYtNC40MS0zLjc4LDMuMDgtMS4wMiw0LjAyLDEuNjgsNS43NiwyLjQ5WiIvPgogICAgPHBhdGggY2xhc3M9ImNscy03IiBkPSJNMTA0LjM4LDYyMS45NGMxLjksMS45NiwxLjEsMi43Ny0xLjM5LDEuNDctMjEuMzYtMTAuNzktMzcuODktMjkuMjgtNDMuMDgtNTIuNjMtMS40OC02LjY4LTIuNTEtMTMuNTMsMS4zLTE5LjYzLDQuMjksMi4xNSw1LjQyLDYuMjUsNi40OCwxMC4xLDYuMjksMjIuNzIsMTguMDEsNDcuMDUsMzYuNjksNjAuNjlaIi8+CiAgICA8cGF0aCBjbGFzcz0iY2xzLTMiIGQ9Ik0xMDIuOTgsNjIzLjQyYy41Ny0uMzgsMS4wNC0uODgsMS4zOS0xLjQ3LDEuNDYsMS4wNywyLjk3LDIuMDIsNC4xNSw0LTIuOTIuODEtNC4wNi0xLjQxLTUuNTQtMi41M1oiLz4KICA8L2c+CiAgPGc+CiAgICA8Zz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMzQ3LjcxLDU1NC4yNHYtMy4yMmMyLjcxLTIuODgsMi45NC03LjAxLDUuNDktMTEuNDIsMTEuMDgsMTAuMTUsNDQuODIsMTMuMzgsNDYuMTItMi41MiwxLjM0LTE2LjMzLTE0LjA5LTEzLjk5LTI5LjA3LTE4LTEzLjA0LTMuNDktMjAuODMtMTQuNDYtMTkuNDktMjYuODMsMS44My0xNi45NywxOS45MS0yMi41NiwzNS44My0yMC43Myw4LjQ0Ljk3LDE2LjY1LDIuMDEsMjMuMDQsOC4zNS0yLjQsNC42MS0zLjYsOC4yOC02LjcsMTIuMzYtNy4wNS04LjUyLTMzLjk0LTEyLjMtMzcuMjguMzUtNS41NCwyMC45Nyw0MC43Nyw2LjY2LDQ3LjM5LDM0LjY1LDIuNCwxMC4xNiwxLjQyLDIwLjk5LTcuMywyNy4wMy0xNy41MywxMi4xMi00MC4zOCwxMC4wNi01OC4wMi0uMDJaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTY1NC4xOCw1NjEuMDdjLTIuMSwyLjI1LTEwLjg1LDMuNjYtMTMuNDMuNTNsLTQ0LjQtNTMuODgtLjU1LDU0LjE2Yy00LjUzLDEuNDMtOC4yMiwxLjM1LTEyLjY0LjY1bC4yNS05Mi4xNiw1Ny42NCw2OC44NS4yOC02OC4wN2M0LjU2LS4zNiw4LjI2LS4zOSwxMi44OS4wMmwtLjA0LDg5LjkxWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTUiIGQ9Ik0xMDIyLjAzLDU1NC42NmwtMzguNDQuMjhjLTIuMTcsMS4zNy0yLjU3LDUuMjMtNC4wOCw3LjQ1LTQuNzUuNi04Ljk4LjY2LTE0LjU2LS4wOWwzNy42Ny05MS40NCwzNy4xMyw4OS45NmMtNC41MSwyLjY2LTkuMywyLjMxLTE0LjExLDEuNTFsLTMuNjMtNy42OFpNMTAxNy44Niw1NDIuMjhsLTE1LjcxLTM4LjI4LTE0LjYzLDM5LjM1YzEwLjk1LS42NCwyMC40MiwxLjQyLDMwLjM0LTEuMDZaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTUxNi44Myw1NTUuMDJsLTM5LjgzLS43MS0zLjY2LDcuOTdjLTUuMDIuMjgtOS4yNy41Mi0xNC42NC0uMTRsMzcuODktOTEuMDIsMzcuMjIsODkuODFjLTQuNDgsMi41My04LjY5LDEuOC0xMy4xMiwxLjA1LTIuMTUtLjE4LTIuMzEtNS43My0zLjg2LTYuOTVaTTQ4MS40Miw1NDIuODhsMzAuNzctLjExLTE2LTM5LjgzYy0zLjIyLDcuMDUtMi44NCwxMy4zLTcuMzYsMTguNTUtMS40NSw3LjYxLTUuMjksMTMuNDQtNy40LDIxLjM5WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05MDIuMzEsNDcyLjY4YzEuNjMtMy44MSwxMC41NC0xLjU4LDE0Ljc2LS4zNGwtMzcuNzgsOTAuODgtMzYuOTQtOTEuMDZjNC4zOC0yLjE1LDkuMzItMS4zMSwxNC41My0uMTZsMjIuNDIsNTQuMzIsMjMuMDEtNTMuNjVaIi8+CiAgICAgIDxnPgogICAgICAgIDxwYXRoIGNsYXNzPSJjbHMtOCIgZD0iTTc3OC41Nyw1MjMuODFjMS44OC0xNy42NS00LjgzLTMxLjg2LTIwLjEtMzcuMDgtMTQuNDMtNC45My0zMC40NC44My0zNy41MywxNi01LjIxLjMzLTkuNjMtMS41LTE1LjQ2LTEuNzIsNy4wMy0xOS42MSwyNy4wMS0zMi4xMiw0Ny40Ni0yOS45MywzNC42NywzLjcyLDQ2Ljk4LDQyLjkxLDM4LjQzLDUyLjUxLTIuMjYsMi41NC0xMi41MSwzLjk1LTEyLjgxLjIyWiIvPgogICAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTc3Ni40LDUzMC43M2M1LjYuOTEsOS43NCwxLjc0LDE1LjMsMS41Ny01LjczLDE2LjI2LTE5LjYxLDI2LjkyLTM0LjY4LDI5Ljc4LTE3LjU1LDMuMzMtMzQuMjctMi44Ny00NC45Mi0xNi44Ni00Ljk3LTYuNTMtMTQuNTktMjcuNzQtNi40NS0zNS4wNiwzLjAzLTIuNzIsNi42OC0yLjc5LDEzLjAzLTEuNzktNS42NiwxOC40NCw3LjI2LDM4Ljc5LDI3Ljg5LDQwLjk4LDEyLjg0LDEuMzYsMjMuNzMtNi45MywyOS44My0xOC42MloiLz4KICAgICAgPC9nPgogICAgPC9nPgogICAgPGc+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTM1MC4wNSw2MDIuMDhjLjk0LjU4LDIuMzIsMS4wNywzLjc4LDEuMDcsMi4xNSwwLDMuNDEtMS4xNCwzLjQxLTIuNzgsMC0xLjUyLS44Ny0yLjQtMy4wNy0zLjI0LTIuNjYtLjk0LTQuMzEtMi4zMi00LjMxLTQuNjIsMC0yLjU0LDIuMTEtNC40Myw1LjI4LTQuNDMsMS42NywwLDIuODguMzksMy42MS44bC0uNTgsMS43MmMtLjUzLS4yOS0xLjYyLS43Ny0zLjEtLjc3LTIuMjMsMC0zLjA3LDEuMzMtMy4wNywyLjQ1LDAsMS41Mi45OSwyLjI4LDMuMjQsMy4xNSwyLjc2LDEuMDcsNC4xNiwyLjQsNC4xNiw0Ljc5LDAsMi41Mi0xLjg2LDQuNy01LjcxLDQuNy0xLjU3LDAtMy4yOS0uNDYtNC4xNi0xLjA0bC41My0xLjc3WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0zODguNzMsNTk2LjMyYzAsNS42Mi0zLjQxLDguNTktNy41OCw4LjU5cy03LjM0LTMuMzQtNy4zNC04LjI4YzAtNS4xOCwzLjIyLTguNTcsNy41OC04LjU3czcuMzQsMy40MSw3LjM0LDguMjZaTTM3Ni4wNyw1OTYuNTljMCwzLjQ5LDEuODksNi42MSw1LjIxLDYuNjFzNS4yMy0zLjA3LDUuMjMtNi43OGMwLTMuMjQtMS42OS02LjYzLTUuMjEtNi42M3MtNS4yMywzLjIyLTUuMjMsNi44WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik00MDMuOTgsNTg4LjMzaDIuMTF2MTQuNTVoNi45N3YxLjc3aC05LjA4di0xNi4zMloiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDI5LjE1LDU4OC4zM3Y5LjY2YzAsMy42NiwxLjYyLDUuMiwzLjgsNS4yLDIuNDIsMCwzLjk3LTEuNiwzLjk3LTUuMnYtOS42NmgyLjEzdjkuNTFjMCw1LjAxLTIuNjQsNy4wNy02LjE3LDcuMDctMy4zNCwwLTUuODYtMS45MS01Ljg2LTYuOTd2LTkuNjFoMi4xM1oiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDY2LjYyLDYwNC4xMmMtLjc3LjM5LTIuMy43Ny00LjI4Ljc3bC0uNTYuOTdjLjkuMTcsMS42OS44MiwxLjY5LDEuODIsMCwxLjQtMS4yMywxLjk2LTIuNDksMS45Ni0uNjMsMC0xLjMxLS4xNy0xLjcyLS40MWwuMzQtMS4wOWMuMzYuMTkuODIuMzIsMS4zNi4zMnMxLjAyLS4yMiwxLjAyLS43M2MwLS42NS0uNzUtLjkyLTEuODktMS4wNGwxLjAyLTEuODZjLTMuOTktLjQ4LTYuODUtMy4zMi02Ljg1LTguMTgsMC01LjExLDMuNDYtOC41Nyw4LjUyLTguNTcsMi4wMywwLDMuMzIuNDQsMy44Ny43M2wtLjUxLDEuNzJjLS44LS4zOS0xLjk0LS42OC0zLjI5LS42OC0zLjgzLDAtNi4zNywyLjQ1LTYuMzcsNi43MywwLDMuOTksMi4zLDYuNTYsNi4yNyw2LjU2LDEuMjgsMCwyLjU5LS4yNywzLjQ0LS42OGwuNDQsMS42N1oiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNDk1LjIxLDU5Ni4zMmMwLDUuNjItMy40MSw4LjU5LTcuNTgsOC41OXMtNy4zNC0zLjM0LTcuMzQtOC4yOGMwLTUuMTgsMy4yMi04LjU3LDcuNTgtOC41N3M3LjM0LDMuNDEsNy4zNCw4LjI2Wk00ODIuNTUsNTk2LjU5YzAsMy40OSwxLjg5LDYuNjEsNS4yMSw2LjYxczUuMjMtMy4wNyw1LjIzLTYuNzhjMC0zLjI0LTEuNjktNi42My01LjIxLTYuNjNzLTUuMjMsMy4yMi01LjIzLDYuOFpNNDg0Ljc1LDU4Ny4yOWMtLjA1LTEuNDguNTgtMi40NywxLjY1LTIuNDcuNTMsMCwuOTIuMTksMS40My40OC4zOS4yMi43Ny40NCwxLjE2LjQ0LjM2LDAsLjU4LS4xNy42NS0uOTRoMS4xMWMuMDIsMS41Mi0uNTEsMi4zNS0xLjYyLDIuMzUtLjUxLDAtLjk0LS4xOS0xLjQ4LS40Ni0uNDYtLjI0LS44LS40Ni0xLjE0LS40Ni0uMzksMC0uNTguNDEtLjYzLDEuMDdoLTEuMTRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTUxOC45MSw1OTdoLTYuMzR2NS44OGg3LjA3djEuNzdoLTkuMTh2LTE2LjMyaDguODF2MS43N2gtNi43MXY1LjE2aDYuMzR2MS43NFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNTM0LjU5LDYwMi4wOGMuOTQuNTgsMi4zMiwxLjA3LDMuNzgsMS4wNywyLjE1LDAsMy40MS0xLjE0LDMuNDEtMi43OCwwLTEuNTItLjg3LTIuNC0zLjA3LTMuMjQtMi42Ni0uOTQtNC4zMS0yLjMyLTQuMzEtNC42MiwwLTIuNTQsMi4xMS00LjQzLDUuMjgtNC40MywxLjY3LDAsMi44OC4zOSwzLjYxLjhsLS41OCwxLjcyYy0uNTMtLjI5LTEuNjItLjc3LTMuMS0uNzctMi4yMywwLTMuMDcsMS4zMy0zLjA3LDIuNDUsMCwxLjUyLjk5LDIuMjgsMy4yNCwzLjE1LDIuNzYsMS4wNyw0LjE2LDIuNCw0LjE2LDQuNzksMCwyLjUyLTEuODYsNC43LTUuNzEsNC43LTEuNTcsMC0zLjI5LS40Ni00LjE2LTEuMDRsLjUzLTEuNzdaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTU3Ni45Nyw1ODguNTJjMS4wMi0uMTcsMi4zNS0uMzEsNC4wNC0uMzEsMi4wOCwwLDMuNjEuNDgsNC41OCwxLjM2LjkuNzcsMS40MywxLjk2LDEuNDMsMy40MXMtLjQ0LDIuNjQtMS4yNiwzLjQ5Yy0xLjExLDEuMTktMi45MywxLjc5LTQuOTksMS43OS0uNjMsMC0xLjIxLS4wMi0xLjY5LS4xNXY2LjU0aC0yLjExdi0xNi4xMlpNNTc5LjA4LDU5Ni4zOWMuNDYuMTIsMS4wNC4xNywxLjc0LjE3LDIuNTQsMCw0LjA5LTEuMjQsNC4wOS0zLjQ5cy0xLjUyLTMuMi0zLjg1LTMuMmMtLjkyLDAtMS42Mi4wNy0xLjk5LjE3djYuMzRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTYwMi45Nyw1OTkuNTJsLTEuNjksNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk02MDguMzIsNTk3Ljg3bC0xLjYtNC43Yy0uMzYtMS4wNy0uNjEtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTYyNy42Niw1ODguNTVjMS4wNy0uMjIsMi41OS0uMzQsNC4wNC0uMzQsMi4yNSwwLDMuNy40MSw0LjcyLDEuMzMuODIuNzMsMS4yOCwxLjg0LDEuMjgsMy4xLDAsMi4xNS0xLjM2LDMuNTgtMy4wNyw0LjE2di4wN2MxLjI2LjQ0LDIuMDEsMS42LDIuNCwzLjI5LjUzLDIuMjguOTIsMy44NSwxLjI2LDQuNDhoLTIuMThjLS4yNy0uNDYtLjYzLTEuODYtMS4wOS0zLjktLjQ4LTIuMjUtMS4zNi0zLjEtMy4yNy0zLjE3aC0xLjk5djcuMDdoLTIuMTF2LTE2LjFaTTYyOS43Nyw1OTUuOThoMi4xNWMyLjI1LDAsMy42OC0xLjI0LDMuNjgtMy4xLDAtMi4xMS0xLjUyLTMuMDMtMy43NS0zLjA1LTEuMDIsMC0xLjc0LjEtMi4wOC4xOXY1Ljk2WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik02NTUuOTYsNTk5LjUybC0xLjY5LDUuMTNoLTIuMThsNS41NC0xNi4zMmgyLjU0bDUuNTcsMTYuMzJoLTIuMjVsLTEuNzQtNS4xM2gtNS43OVpNNjYxLjMxLDU5Ny44N2wtMS42LTQuN2MtLjM2LTEuMDctLjYtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTcxMC43MSw2MDMuOTJjLS45NC4zNC0yLjgxLjktNS4wMS45LTIuNDcsMC00LjUtLjYzLTYuMS0yLjE1LTEuNC0xLjM2LTIuMjgtMy41My0yLjI4LTYuMDguMDItNC44NywzLjM3LTguNDIsOC44NC04LjQyLDEuODksMCwzLjM2LjQxLDQuMDcuNzVsLS41MSwxLjcyYy0uODctLjM5LTEuOTYtLjctMy42MS0uNy0zLjk3LDAtNi41NiwyLjQ3LTYuNTYsNi41NnMyLjQ5LDYuNTgsNi4yOSw2LjU4YzEuMzgsMCwyLjMyLS4xOSwyLjgxLS40NHYtNC44N2gtMy4zMnYtMS42OWg1LjM3djcuODRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTczNC44OSw1OTdoLTYuMzR2NS44OGg3LjA3djEuNzdoLTkuMTd2LTE2LjMyaDguODF2MS43N2gtNi43MXY1LjE2aDYuMzR2MS43NFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNzUwLjU3LDYwMi4wOGMuOTQuNTgsMi4zMiwxLjA3LDMuNzgsMS4wNywyLjE1LDAsMy40MS0xLjE0LDMuNDEtMi43OCwwLTEuNTItLjg3LTIuNC0zLjA3LTMuMjQtMi42Ni0uOTQtNC4zMS0yLjMyLTQuMzEtNC42MiwwLTIuNTQsMi4xMS00LjQzLDUuMjgtNC40MywxLjY3LDAsMi44OC4zOSwzLjYxLjhsLS41OCwxLjcyYy0uNTMtLjI5LTEuNjItLjc3LTMuMS0uNzctMi4yMywwLTMuMDcsMS4zMy0zLjA3LDIuNDUsMCwxLjUyLjk5LDIuMjgsMy4yNCwzLjE1LDIuNzYsMS4wNyw0LjE2LDIuNCw0LjE2LDQuNzksMCwyLjUyLTEuODYsNC43LTUuNzEsNC43LTEuNTcsMC0zLjI5LS40Ni00LjE2LTEuMDRsLjUzLTEuNzdaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTc3OC40MSw1OTAuMTJoLTQuOTZ2LTEuNzloMTIuMDh2MS43OWgtNC45OXYxNC41M2gtMi4xM3YtMTQuNTNaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTgwMC42OCw1OTkuNTJsLTEuNjksNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk04MDAuNjgsNTg3LjM0Yy0uMDItMS40OC42MS0yLjQ3LDEuNjUtMi40Ny41MywwLC45NC4yMiwxLjQ1LjQ4LjM5LjIyLjc3LjQ0LDEuMTQuNDQuMzksMCwuNi0uMTcuNjUtLjk0aDEuMTRjLjAyLDEuNTMtLjUxLDIuMzUtMS42NSwyLjM1LS41MSwwLS45NC0uMTktMS40OC0uNDYtLjQ2LS4yNC0uNzctLjQ2LTEuMTQtLjQ2LS4zOSwwLS41Ni40MS0uNjMsMS4wN2gtMS4xNFpNODA2LjAzLDU5Ny44N2wtMS42LTQuN2MtLjM2LTEuMDctLjYtMi4wMy0uODUtMi45OGgtLjA1Yy0uMjQuOTctLjUxLDEuOTYtLjgyLDIuOTVsLTEuNiw0LjcyaDQuOTFaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTgzOC45NSw1OTYuMzJjMCw1LjYyLTMuNDEsOC41OS03LjU4LDguNTlzLTcuMzQtMy4zNC03LjM0LTguMjhjMC01LjE4LDMuMjItOC41Nyw3LjU4LTguNTdzNy4zNCwzLjQxLDcuMzQsOC4yNlpNODI2LjI5LDU5Ni41OWMwLDMuNDksMS44OSw2LjYxLDUuMiw2LjYxczUuMjMtMy4wNyw1LjIzLTYuNzhjMC0zLjI0LTEuNjktNi42My01LjItNi42M3MtNS4yMywzLjIyLTUuMjMsNi44WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik04NzEuODQsNTg4LjU1YzEuMjgtLjE5LDIuODEtLjM0LDQuNDgtLjM0LDMuMDMsMCw1LjE4LjcsNi42MSwyLjAzLDEuNDUsMS4zMywyLjMsMy4yMiwyLjMsNS44NnMtLjgyLDQuODQtMi4zNSw2LjM0Yy0xLjUyLDEuNTItNC4wNCwyLjM1LTcuMjEsMi4zNS0xLjUsMC0yLjc2LS4wNy0zLjgzLS4xOXYtMTYuMDVaTTg3My45NSw2MDIuOThjLjUzLjEsMS4zMS4xMiwyLjEzLjEyLDQuNSwwLDYuOTUtMi41Miw2Ljk1LTYuOTIuMDItMy44NS0yLjE1LTYuMjktNi42MS02LjI5LTEuMDksMC0xLjkxLjEtMi40Ny4yMnYxMi44OFoiLz4KICAgICAgPHBhdGggY2xhc3M9ImNscy0xIiBkPSJNOTAyLjc4LDU5OS41MmwtMS42OSw1LjEzaC0yLjE4bDUuNTQtMTYuMzJoMi41NGw1LjU3LDE2LjMyaC0yLjI1bC0xLjc0LTUuMTNoLTUuNzlaTTkwOC4xMyw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42LTIuMDMtLjg1LTIuOThoLS4wNWMtLjI0Ljk3LS41MSwxLjk2LS44MiwyLjk1bC0xLjYsNC43Mmg0LjkxWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05NDcuNzUsNTk5LjUybC0xLjcsNS4xM2gtMi4xOGw1LjU0LTE2LjMyaDIuNTRsNS41NywxNi4zMmgtMi4yNWwtMS43NC01LjEzaC01Ljc5Wk05NTMuMSw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42MS0yLjAzLS44NS0yLjk4aC0uMDVjLS4yNC45Ny0uNTEsMS45Ni0uODIsMi45NWwtMS42LDQuNzJoNC45MVpNOTU0LjI2LDU4NC42M2wtMy4wNywyLjgzaC0xLjc0bDIuMjUtMi44M2gyLjU3WiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik05ODQuNSw2MDMuOTJjLS45NC4zNC0yLjgxLjktNS4wMS45LTIuNDcsMC00LjUtLjYzLTYuMS0yLjE1LTEuNC0xLjM2LTIuMjgtMy41My0yLjI4LTYuMDguMDItNC44NywzLjM3LTguNDIsOC44NC04LjQyLDEuODksMCwzLjM3LjQxLDQuMDcuNzVsLS41MSwxLjcyYy0uODctLjM5LTEuOTYtLjctMy42MS0uNy0zLjk3LDAtNi41NiwyLjQ3LTYuNTYsNi41NnMyLjQ5LDYuNTgsNi4yOSw2LjU4YzEuMzgsMCwyLjMyLS4xOSwyLjgxLS40NHYtNC44N2gtMy4zMnYtMS42OWg1LjM3djcuODRaIi8+CiAgICAgIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTEwMDIuMzMsNTg4LjMzdjkuNjZjMCwzLjY2LDEuNjIsNS4yLDMuOCw1LjIsMi40MiwwLDMuOTctMS42LDMuOTctNS4ydi05LjY2aDIuMTN2OS41MWMwLDUuMDEtMi42NCw3LjA3LTYuMTcsNy4wNy0zLjM0LDAtNS44Ni0xLjkxLTUuODYtNi45N3YtOS42MWgyLjEzWiIvPgogICAgICA8cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMDMwLjIyLDU5OS41MmwtMS43LDUuMTNoLTIuMThsNS41NC0xNi4zMmgyLjU0bDUuNTcsMTYuMzJoLTIuMjVsLTEuNzQtNS4xM2gtNS43OVpNMTAzNS41Nyw1OTcuODdsLTEuNi00LjdjLS4zNi0xLjA3LS42MS0yLjAzLS44NS0yLjk4aC0uMDVjLS4yNC45Ny0uNTEsMS45Ni0uODIsMi45NWwtMS42LDQuNzJoNC45MVoiLz4KICAgIDwvZz4KICA8L2c+Cjwvc3ZnPg==';
    document.head.appendChild(link);
    </script>
    ''')
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:28px;padding:16px 0 12px 0;">
        <img src="{LOGO_SVG}" style="height:110px;width:auto;flex-shrink:0;" alt="SANOVA">
        <div style="display:flex;flex-direction:column;gap:6px;justify-content:center;">
            <p style="font-size:2.6rem;font-weight:800;color:#2980B9;margin:0;padding:0;line-height:1.1;font-family:inherit;">Análise Comercial de Micromedição</p>
            <p style="font-size:1.15rem;color:#9BA0A6;margin:0;font-weight:400;font-family:inherit;">SANOVA | saneamento inteligente</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_filters(df, qm):
    with st.sidebar:
        chat.render(df)

        st.divider()

        st.markdown("### Filtros Globais")

        with st.expander("📂 Categorias", expanded=False):
            cats_all = df['CATEGORIA_PRINCIPAL'].unique().tolist()
            categorias = []
            for i, cat in enumerate(cats_all):
                if st.checkbox(cat, value=True, key=f'cat_{i}'):
                    categorias.append(cat)

        with st.expander("🔌 Situação da Ligação", expanded=False):
            sits_all = df['SIT._LIG_AGUA'].unique().tolist()
            situacoes = []
            for i, sit in enumerate(sits_all):
                if st.checkbox(sit, value=True, key=f'sit_{i}'):
                    situacoes.append(sit)

        with st.expander("🏷️ Marca do Hidrômetro", expanded=False):
            marcas_all = df['MARCA_HIDROMETRO'].dropna().unique().tolist()
            marcas = []
            for i, mar in enumerate(marcas_all):
                if st.checkbox(mar, value=True, key=f'mar_{i}'):
                    marcas.append(mar)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)

        st.markdown("#### Resumo dos Dados")

        iqd_pct = qm['iqd']
        iqd_badge = "sucesso" if iqd_pct >= 90 else ("alerta" if iqd_pct >= 70 else "critico")
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-title">Qualidade dos Dados</div>
            <div>
                IQD: <span class="info-badge {iqd_badge}">{iqd_pct}%</span>
            </div>
            <div style="margin-top:4px; font-size:0.85rem; color:#7F8C8D;">
                {qm['registros_completos']:,} registros completos de {qm['total_registros']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

        anom_count = qm['anomalias_leitura'] + qm['outliers_extremos']
        anom_badge = "critico" if anom_count > 50 else ("alerta" if anom_count > 0 else "sucesso")
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-title">Oportunidades</div>
            <div style="font-size:0.85rem;">
                Casos críticos: <span class="info-badge {anom_badge}">{anom_count}</span>
            </div>
            <div style="font-size:0.85rem; margin-top:4px; color:#7F8C8D;">
                Receita potencial: R$ 2.49M
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)
        st.markdown("#### Opções de Visualização")

        include_outliers = st.checkbox("Incluir outliers extremos", value=True)
        dados_completos_only = st.checkbox("Apenas dados completos", value=False)

        st.markdown("<hr class='divider-custom'>", unsafe_allow_html=True)
        st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.caption(f"Período: 13 meses")

        return categorias, situacoes, marcas, include_outliers, dados_completos_only


def main():
    st.set_page_config(
        page_title="Micromedicao | Analise Comercial | SANOVA",
        layout="wide",
        page_icon="💧"
    )

    render_header()

    df = load_data(DATA_FILE)
    qm = get_quality_metrics(df)

    categorias, situacoes, marcas, include_outliers, dados_completos_only = render_sidebar_filters(df, qm)

    if not include_outliers:
        df = df[~df.get('FLAG_OUTLIER_EXTREMO', pd.Series([False]*len(df)))]

    if dados_completos_only:
        df = df[df['MESES_DADOS_AUSENTES'] == 0]

    df_filtered = apply_filters(df, categorias, situacoes, marcas)

    st.markdown(f"""
    <div style="margin-bottom:8px; font-size:0.85rem; color:#7F8C8D;">
        Registros filtrados: <strong>{len(df_filtered):,}</strong> de {len(df):,} no total
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral",
        "🚨 Anomalias & Fraudes",
        "📉 Consumo Zero",
        "🔧 Hidrômetros",
        "💰 Recuperação de Receita",
        "🔍 Qualidade de Dados"
    ])

    with tab1:
        overview.render(df_filtered, qm)
        render_methodology_expander()

    with tab2:
        anomalies.render(df_filtered)
        render_methodology_expander()

    with tab3:
        zero_consumption.render(df_filtered)
        render_methodology_expander()

    with tab4:
        meters.render(df_filtered)
        render_methodology_expander()

    with tab5:
        recovery.render(df_filtered)
        render_methodology_expander()

    with tab6:
        data_quality.render(df_filtered, qm)
        render_methodology_expander()


if __name__ == "__main__":
    main()