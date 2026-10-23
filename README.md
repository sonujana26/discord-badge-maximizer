<div align="center">

# Discord Badge Maximizer

**A lightweight, pure Python telemetry and activity engine for Discord profile badges**

<p align="center">
  <a href="https://discord.gg/JaBugGHQ4m"><img src="https://img.shields.io/badge/Discord-Join%20Support-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Support" /></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge" alt="License: MIT" /></a>
</p>

<p align="center">
  <a href="#1-maximize-game-variety--game-time-badges-gamespy"><img src="https://img.shields.io/badge/Maximize%20Game%20Variety-%E2%9C%93%20Supported-success?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIj48cGF0aCBmaWxsPSIjRkZCQTU0IiBkPSJtOC43NyA0LjU2LS41LS43NmMtLjE1LS4yMy0uMzgtLjM0LS42LS4yOUw1LjggNGMtLjQuMS0uNzMuNDktLjg4IDEuMDNsLS4yNC43OXMtLjE1LjUgMCAuNTJNMTUuMjMgNC41NmwuNS0uNzZjLjE1LS4yMy4zOC0uMzQuNi0uMjlMMTguMiA0Yy40LjEuNzMuNDkuODggMS4wM2wuMjQuNzlzLjE1LjUgMCAuNTIiLz48cGF0aCBmaWxsPSJ1cmwoI2EpIiBkPSJNMjAuNDQgOC4yMWMtMS00LjA3LTQuNzktMy42OC00Ljc5LTMuNjhoLTcuM3MtMy44LS4zOS00Ljc5IDMuNjhjLTEgNC4wNy0zLjIgMTAuOTIuNTQgMTEuNzMgMCAwIDEuNjIuNTggMi44Ny0xLjkxIDEuMjUtMi41IDEuNDYtMi44OCAzLjgtMi44OGgyLjQ3YzIuMzMgMCAyLjU0LjM5IDMuNzkgMi44OCAxLjI1IDIuNDkgMi44NyAxLjkxIDIuODcgMS45MSAzLjc1LS44MSAxLjU0LTcuNjYuNTQtMTEuNzNaIi8%2BPHBhdGggZmlsbD0iI0ZGRUIzQSIgZD0iTTMuODIgOS44cy4xMiAxLjYgNC45NSAxLjZjMCAwLTUuMi43NC01Ljk1IDIuMjUtLjc1IDEuNS41LTMuNzEgMS0zLjg0Wk0yMC4yNSA5LjhzLS4xMyAxLjYtNC45NiAxLjZjMCAwIDUuMTUuNDQgNS45IDEuOTQuNzYgMS41LS40Ni0zLjQtLjk0LTMuNTNaTTYuMSAzLjkybC0uMy4wN2MtLjQuMS0uNzMuNDktLjg4IDEuMDNsLS4yNC43OXMtLjE1LjUgMCAuNTJsLjE5LS4wOGMtLjAzLS4xNC4yLS40Mi4yLS40MmwuMjMtLjgyYy4xNi0uNTQuNC0xIC44LTEuMVoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJtMjAuNTQgOS4xNi0uMDMtLjEuMDMuMVoiLz48cGF0aCBmaWxsPSIjRkZFQjNBIiBkPSJNNC4xMiA4LjY0YzEtNC4wNyA0LjU1LTMuODMgNC41NS0zLjgzaDcuM3MxLjctLjE3IDMuMTIuOTNjLTEuNDctMS40MS0zLjQ0LTEuMjEtMy40NC0xLjIxaC03LjNzLTMuOC0uMzktNC43OSAzLjY4Yy0uOSAzLjY4LTIuOCA5LjY0LS4zOCAxMS4zNC0xLjktMiAuMDgtNy40MS45NC0xMC45MVoiLz48cGF0aCBmaWxsPSIjQjM0QzAwIiBkPSJNMTYuNzUgMTAuMTZjLjU4IDAgMS4wNi0uNSAxLjA2LTEuMSAwLS42LS40OC0xLjEtMS4wNi0xLjEtLjYgMC0xLjA3LjUtMS4wNyAxLjEgMCAuNi40OCAxLjEgMS4wNyAxLjFaTTE2Ljc1IDE0LjE0Yy41OCAwIDEuMDYtLjQ5IDEuMDYtMS4xIDAtLjYtLjQ4LTEuMS0xLjA2LTEuMS0uNiAwLTEuMDcuNS0xLjA3IDEuMSAwIC42MS40OCAxLjEgMS4wNyAxLjFaTTE0LjgxIDEyLjE1Yy42IDAgMS4wNy0uNDkgMS4wNy0xLjEgMC0uNi0uNDgtMS4xLTEuMDctMS4xLS41OSAwLTEuMDYuNS0xLjA2IDEuMSAwIC42MS40NyAxLjEgMS4wNiAxLjFaTTE4LjY4IDEyLjE1Yy41OSAwIDEuMDYtLjQ5IDEuMDYtMS4xIDAtLjYtLjQ3LTEuMS0xLjA2LTEuMS0uNiAwLTEuMDcuNS0xLjA3IDEuMSAwIC42MS40OCAxLjEgMS4wNyAxLjFaIi8%2BPHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyLjk4IDUuODNoLTIuMDRhLjc2Ljc2IDAgMCAwLS43Ni43N2MwIC40Mi4zNC43Ni43Ni43NmgyLjA0Yy40MiAwIC43NS0uMzQuNzUtLjc2YS43Ni43NiAwIDAgMC0uNzUtLjc3WiIvPjxwYXRoIGZpbGw9IiNCMzRDMDAiIGQ9Ik05LjQzIDEwLjA2SDguMTlWOC44M2MwLS40LS4zMi0uNzEtLjctLjcxaC0uNDZjLS40IDAtLjcuMzItLjcuNzF2MS4yM0g1LjA3YS43LjcgMCAwIDAtLjY5Ljd2LjVjMCAuMzguMzEuNjkuNjkuNjloMS4yNHYxLjIzYzAgLjQuMzIuNzEuNy43MWguNDZjLjQgMCAuNy0uMzIuNy0uNzF2LTEuMjNoMS4yNWEuNy43IDAgMCAwIC42OS0uN3YtLjVhLjcuNyAwIDAgMC0uNjktLjY5WiIvPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iYSIgeDE9IjEyIiB4Mj0iMTIiIHkxPSI0LjUyIiB5Mj0iMjAiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBzdG9wLWNvbG9yPSIjRkY4MDAwIi8%2BPHN0b3Agb2Zmc2V0PSIuMTIiIHN0b3AtY29sb3I9IiNGQTAiLz48c3RvcCBvZmZzZXQ9Ii40OCIgc3RvcC1jb2xvcj0iI0Y2RkYzQSIvPjxzdG9wIG9mZnNldD0iLjY3IiBzdG9wLWNvbG9yPSIjRjkwIi8%2BPHN0b3Agb2Zmc2V0PSIuOTUiIHN0b3AtY29sb3I9IiNFNDREMDIiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48L3N2Zz4=" alt="Maximize Game Variety" /></a>
  <a href="#1-maximize-game-variety--game-time-badges-gamespy"><img src="https://img.shields.io/badge/Maximize%20Game%20Time-%E2%9C%93%20Supported-success?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIj48cGF0aCBmaWxsPSJ1cmwoI2EpIiBkPSJtMTAuODUgMTcuNzUtNC40NS00LjUgOS4xLTkuMmMuMTctLjE3LjM5LS4yOC42Mi0uMzJsNC4zNS0uNzJjLjMtLjA2LjU3LjIyLjUyLjUzbC0uNzEgNC4zOWMtLjA0LjI0LS4xNS40Ni0uMzIuNjNsLTkuMSA5LjJaIi8%2BPHBhdGggZmlsbD0idXJsKCNiKSIgZD0iTTIxIDMuNTRhLjQ2LjQ2IDAgMCAwLS4xNC0uNEw4LjYzIDE1LjVsMi4yMiAyLjI1IDkuMS05LjJjLjE4LS4xNi4yOS0uMzguMzMtLjYybC43MS00LjRaIi8%2BPHBhdGggZmlsbD0idXJsKCNjKSIgZD0ibTIwLjQ3IDMtNC4zNS43M2MtLjIzLjA0LS40NC4xNC0uNi4zdi4wMWwtLjAyLjAxLS4xMy4xNC40NSA0LjA0IDUuMDQtNS4xYS40NS40NSAwIDAgMC0uNC0uMTJaIi8%2BPHBhdGggZmlsbD0iI0ZGQUUwMyIgZD0iTTE5Ljk4IDguNTRjLjE1LS4xNy4yNi0uMzguMy0uNjFsLjcxLTQuNGEuNDYuNDYgMCAwIDAtLjEzLS40bC01LjA0IDUuMSA0IC40Ni4xNi0uMTVaIi8%2BPHBhdGggZmlsbD0iI0ZGREQzNiIgZD0ibTIwLjQ3IDMtNC4zNS43M2MtLjIyLjA0LS40My4xNC0uNi4zdi4wMWwtLjAyLjAxLS4xMy4xNC40NSA0LjA0IDUuMDUtNS4xYS40NS40NSAwIDAgMC0uNC0uMTJaIi8%2BPHBhdGggZmlsbD0idXJsKCNkKSIgZD0ibTcuNDYgMTQuNiA5LjExLTkuMiAyLjQ3LS40Mi0uNCAyLjUtOS4xMiA5LjItMi4wNi0yLjA4WiIvPjxwYXRoIGZpbGw9InVybCgjZSkiIGQ9Im0xMC4wOSAxNi4xNS0yLjMtMi4zMS0zLjgyIDMuODcgMi4yOCAyLjMxIDMuODQtMy44N1oiLz48cGF0aCBmaWxsPSIjRkY5QTBEIiBkPSJtNi4yNSAyMC4wMi0yLjI4LTIuMy0uNDItLjFjLS4wOS0uMDItLjE2IDAtLjIxLjA1bC0uMjkuMjlhLjIuMiAwIDAgMC0uMDUuMTVsLjA3IDEuNjFjLjAzLjU3LjY0IDEuMTggMS4yIDEuMmwxLjU5LjA4YS4yLjIgMCAwIDAgLjE1LS4wNWwuMjktLjNjLjA0LS4wNC4wNi0uMTIuMDQtLjJsLS4wOS0uNDNaIi8%2BPHBhdGggZmlsbD0iI0IzNEMwMCIgZD0iTTEwLjA5IDE2LjE1IDguOSAxNy4zNGMtLjM2LS4zNC0uNzMtLjctMS4wNy0xLjA1LS40LS40LS44My0uODQtMS4yLTEuMjdsMS4xNi0xLjE4IDIuMjkgMi4zMVoiLz48cGF0aCBmaWxsPSJ1cmwoI2YpIiBkPSJNNi4xNCAxMy41MmEuODMuODMgMCAwIDAtLjk0LS4yMi42OC42OCAwIDAgMS0uOS0uNDJsLS4zLS45YS45LjkgMCAwIDEgLjItLjkybC45LS45MWMuMzUtLjM1IDEuMS0xLjA3IDEuNjguNi4yLjU3LjYgMS4xOSAxLjA2IDEuNzYgMCAwIC4zNC42IDEuODQgMi4xMyAxLjUgMS41MiAyLjQ5IDIuMSAyLjQ5IDIuMS4zOS4yNy43OS41IDEuMTYuNjMgMS42NS41OC45NCAxLjM0LjYgMS42OWwtLjkuOTFhLjg3Ljg3IDAgMCAxLS45MS4yMWwtLjktLjNhLjcuNyAwIDAgMS0uNDEtLjkzLjg0Ljg0IDAgMCAwLS4yMi0uOTRzLTEuMDItLjgyLTIuMzItMi4xNGMtMS4zMS0xLjMyLTIuMTMtMi4zNS0yLjEzLTIuMzVaIi8%2BPHBhdGggZmlsbD0iI2ZmZiIgZD0iTTExLjUyIDEwLjVoNC4xMmwxLjg4LTEuOTFIMTMuNGwtMS44OCAxLjlaIi8%2BPGRlZnM%2BPGxpbmVhckdyYWRpZW50IGlkPSJhIiB4MT0iMTMuNyIgeDI9IjEzLjciIHkxPSIzIiB5Mj0iMTcuNzUiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBzdG9wLWNvbG9yPSIjRkZCQjU0Ii8%2BPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjRkM2NjBFIi8%2BPC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImIiIHgxPSIxNC44MSIgeDI9IjE0LjgxIiB5MT0iMy4xNCIgeTI9IjE3Ljc1IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI%2BPHN0b3Agb2Zmc2V0PSIuMzQiIHN0b3AtY29sb3I9IiNGM0ZENDAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNGQzY2MEUiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYyIgeDE9IjE4LjEyIiB4Mj0iMTguMTIiIHkxPSIzIiB5Mj0iOC4yMyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIHN0b3AtY29sb3I9IiNGM0ZENDAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNGQzY2MEUiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iZCIgeDE9IjEzLjI1IiB4Mj0iMTMuMjUiIHkxPSI0Ljk4IiB5Mj0iMTYuNjgiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBzdG9wLWNvbG9yPSIjRkYwIi8%2BPHN0b3Agb2Zmc2V0PSIuNzMiIHN0b3AtY29sb3I9IiNGRkMzNEIiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iZSIgeDE9IjguOTQiIHgyPSI1LjA3IiB5MT0iMTUiIHkyPSIxOC44MyIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIHN0b3AtY29sb3I9IiNGRjFDMkYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNGMkZGNDEiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iZiIgeDE9IjkuMTYiIHgyPSI5LjE2IiB5MT0iOS42OSIgeTI9IjIwLjIzIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI%2BPHN0b3Agc3RvcC1jb2xvcj0iI0ZCNjcwRSIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI0RCMDAxMiIvPjwvbGluZWFyR3JhZGllbnQ%2BPC9kZWZzPjwvc3ZnPg==" alt="Maximize Game Time" /></a>
  <a href="#2-maximize-stream-time-badge-streampy"><img src="https://img.shields.io/badge/Maximize%20Stream%20Time-%E2%9C%93%20Supported-success?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIj48cGF0aCBmaWxsPSJ1cmwoI2EpIiBkPSJNMTcgMTkuOTdjLjM4LjQuMSAxLjAzLS40NSAxLjAzaC05LjFjLS41NCAwLS44My0uNjQtLjQ2LTEuMDNoMTAuMDJaIi8%2BPHBhdGggZmlsbD0iI0ZGOUEwRCIgZD0iTTguMjQgMTguOTRhLjYzLjYzIDAgMCAwLS40Ni4ybC0uNzkuODNhLjYuNiAwIDAgMC0uMTYuMzZoMTAuMzRhLjU5LjU5IDAgMCAwLS4xNi0uMzZsLS43OS0uODNhLjY0LjY0IDAgMCAwLS40Ni0uMkg4LjI0WiIvPjxwYXRoIGZpbGw9InVybCgjYikiIGQ9Ik05LjEzIDEzLjc2aDUuNzR2NS41OWMwIC4yNC0uMi40NC0uNDQuNDRIOS41OGEuNDUuNDUgMCAwIDEtLjQ1LS40NHYtNS42WiIvPjxwYXRoIGZpbGw9IiM4NzM3MDAiIGQ9Ik0xNC44NyAxNi4zSDkuMTN2MS43OGg1Ljc0VjE2LjNaIi8%2BPHBhdGggZmlsbD0idXJsKCNjKSIgZD0ibTIwLjg1IDE1LjkyLTEuMDggMS4zN2EuOS45IDAgMCAxLS43LjNINC45M2EuOS45IDAgMCAxLS43LS4zbC0xLjA4LTEuMzdoMTcuN1oiLz48cGF0aCBmaWxsPSJ1cmwoI2QpIiBkPSJtMjAuMTIgMy44OC44OCAxMS41Yy4wNC42LS41OCAxLjEtMS40IDEuMUg0LjRjLS44MiAwLTEuNDQtLjUtMS40LTEuMWwuODgtMTEuNUMzLjkyIDMuNCA0LjUzIDMgNS4yNiAzaDEzLjQ4Yy43MyAwIDEuMzQuNCAxLjM4Ljg4WiIvPjxwYXRoIGZpbGw9InVybCgjZSkiIGQ9Ik0yMC4xMiAzLjg4Yy0uMDQtLjQ5LS42NS0uODgtMS4zOC0uODhINS4yNmMtLjczIDAtMS4zNC40LTEuMzguODhsLS4yIDIuNjZjMTItMS43NyAxNS45NiAyLjk0IDE3IDQuN2wtLjU2LTcuMzZaIi8%2BPHBhdGggZmlsbD0iIzg3MzcwMCIgZD0ibTE4LjE5IDQuODQuNiA5LjQ3Yy4wMS4yMy0uMjIuNDEtLjUyLjQxSDUuNzNjLS4zIDAtLjUzLS4xOC0uNTItLjRsLjYtOS40OGMuMDEtLjE4LjI0LS4zMy41Mi0uMzNoMTEuMzRjLjI3IDAgLjUuMTUuNTIuMzNaIi8%2BPHBhdGggZmlsbD0idXJsKCNmKSIgZD0ibTE4LjAzIDE0LjcyLS40NS05LjE2Yy0uMDEtLjE4LS4yMi0uMzMtLjQ3LS4zM0g2LjljLS4yNSAwLS40Ni4xNS0uNDcuMzNsLS40NSA5LjE2aDEyLjA2WiIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik02Ljg5IDUuMjNjLS4yNSAwLS40Ni4xNS0uNDcuMzNsLS4wNiAxLjNjNS44Ni0uMjggOS40NSAxLjEzIDExLjQgMi4zMmwtLjE4LTMuNjJjLS4wMS0uMTgtLjIyLS4zMy0uNDYtLjMzSDYuODlaIi8%2BPGRlZnM%2BPGxpbmVhckdyYWRpZW50IGlkPSJhIiB4MT0iMTIiIHgyPSIxMiIgeTE9IjIxLjciIHkyPSIxMy4xMSIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIHN0b3AtY29sb3I9IiNGRjFDMkYiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNGMkZGNDEiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iYiIgeDE9IjEyIiB4Mj0iMTIiIHkxPSIyMi40IiB5Mj0iNS4yIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI%2BPHN0b3Agc3RvcC1jb2xvcj0iI0ZGMUMyRiIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI0YyRkY0MSIvPjwvbGluZWFyR3JhZGllbnQ%2BPGxpbmVhckdyYWRpZW50IGlkPSJjIiB4MT0iMTIiIHgyPSIxMiIgeTE9IjIyLjQiIHkyPSI1LjIiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBzdG9wLWNvbG9yPSIjRkYxQzJGIi8%2BPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjRjJGRjQxIi8%2BPC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImQiIHgxPSIxMiIgeDI9IjEyIiB5MT0iMTkuODMiIHkyPSI1LjMiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj48c3RvcCBzdG9wLWNvbG9yPSIjRjNGRDQwIi8%2BPHN0b3Agb2Zmc2V0PSIuMDEiIHN0b3AtY29sb3I9IiNGM0Y5M0UiLz48c3RvcCBvZmZzZXQ9Ii4xOCIgc3RvcC1jb2xvcj0iI0Y1Q0MzMCIvPjxzdG9wIG9mZnNldD0iLjM1IiBzdG9wLWNvbG9yPSIjRjhBNzIzIi8%2BPHN0b3Agb2Zmc2V0PSIuNTEiIHN0b3AtY29sb3I9IiNGOThBMUEiLz48c3RvcCBvZmZzZXQ9Ii42OCIgc3RvcC1jb2xvcj0iI0ZCNzYxMyIvPjxzdG9wIG9mZnNldD0iLjg0IiBzdG9wLWNvbG9yPSIjRkI2QTBGIi8%2BPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjRkM2NjBFIi8%2BPC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImUiIHgxPSIxMi4xOCIgeDI9IjEyLjE4IiB5MT0iMTEuNDciIHkyPSIyLjA2IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI%2BPHN0b3Agc3RvcC1jb2xvcj0iI0ZGMCIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI0ZGQzM0QiIvPjwvbGluZWFyR3JhZGllbnQ%2BPGxpbmVhckdyYWRpZW50IGlkPSJmIiB4MT0iMTIiIHgyPSIxMiIgeTE9IjE1LjAxIiB5Mj0iNi42NSIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIHN0b3AtY29sb3I9IiNGRjAiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNGRkREMzYiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48L3N2Zz4=" alt="Maximize Stream Time" /></a>
</p>

<p align="center">
  Programmatically level up your <b>Game Time</b>, <b>Game Variety</b>, and <b>Streaming</b> progression badges by interacting directly with Discord's analytics telemetry endpoint (<code>/api/v9/science</code>) and Voice Gateway protocol.
</p>

*Zero external dependencies • Standard library only • Multi-vector engine*

</div>

---

## Contents

- [What it does](#what-it-does)
- [Features and Tools 🌟](#features-and-tools-)
- [Badges Supported & Tiers](#badges-supported--tiers)
- [How to Obtain Credentials](#how-to-obtain-credentials)
  - [Step 1: Discord Account Token](#step-1-discord-account-token)
  - [Step 2: Cloudflare Clearance Cookie (`cf_clearance`)](#step-2-cloudflare-clearance-cookie-cf_clearance)
- [Step-by-Step Usage Guide](#step-by-step-usage-guide)
  - [1. Maximize Game Variety & Game Time Badges (`games.py`)](#1-maximize-game-variety--game-time-badges-gamespy)
  - [2. Maximize Stream Time Badge (`stream.py`)](#2-maximize-stream-time-badge-streampy)
  - [Live Profile & Badge Inspection (Both Scripts)](#live-profile--badge-inspection-both-scripts)
- [How It Works](#how-it-works)
- [Important Disclaimer](#important-disclaimer)

---

## What it does

Discord tracks user game activity and broadcast hours to award tiered profile progression badges:

- **Game Activity Telemetry:** Discord's desktop client dispatches telemetry events (`launch_game` and `running_game_heartbeat`) to `/api/v9/science`. Because Discord does not run game executables on its servers, the backend trusts authenticated client reports for `duration_tracked_ms`.
- **Stream Activity & Gateway:** The streaming badge tracks hours spent sharing your screen or broadcasting via Go Live in voice channels. Progress is calculated via client telemetry (`video_stream_started`, `video_stream_ended`) and live voice state connections (`STREAM_CREATE` Opcode 18).

This repository provides standalone tools to simulate authentic telemetry packets and maintain headless Go Live broadcasts without running resource-heavy games, GPUs, or software.

---

## Features and Tools 🌟

<details open>
<summary><b>Features ✨ (Click to expand)</b></summary>

- ☑️ **Instant Science Telemetry Forge:** Emits authentic client-side stream and game telemetry events directly to `/api/v9/science`.
- ☑️ **Realistic Historical Session Builder:** Decomposes target hours into organic multi-hour sessions across days/weeks with randomized viewer counts and game titles.
- ☑️ **Headless Gateway AFK Streamer:** Connects directly to Discord Gateway, joins a voice channel, and triggers Opcode 18 `STREAM_CREATE` for real 24/7 Go Live status with **0% CPU and 0% GPU usage**.
- ☑️ **Automated Game Catalog Integration:** Synchronizes with Discord's detectable games list to rotate through hundreds of verified titles for the Game Variety badge.
- ☑️ **Live Profile & Badge Inspector:** Queries Discord's user profile API to display current badge tiers and equipped collectibles directly in your console.
- ☑️ **Shared Authentication State:** Saves your session securely to `session.json` so you only have to provide auth once across both scripts.
- ☑️ **Zero Dependencies:** Pure Python standard library (Python 3.10+). No `pip install` required.

</details>

---

## Badges Supported & Tiers

| Badge | Criteria | Maximum Milestone | Progression Track |
| :--- | :--- | :--- | :--- |
| ⭐ **Game Time** | Cumulative hours spent playing detectable games | **5,000+ hours** | 10 progressive tiers (Casual &rarr; Eternal) |
| ⭐ **Game Variety** | Count of unique detectable games launched | **100+ games** | 10 progressive tiers (Sampler &rarr; Universalist) |
| ⭐ **Streaming** | Hours spent streaming video in voice channels | **5,000+ hours** | 10 progressive tiers (Newcomer &rarr; Phenomenon) |

<details>
<summary><b>View Streaming Badge Tiers (Click to expand)</b></summary>

| Tier | Name | Target Hours |
| :---: | :--- | :---: |
| **1** | Newcomer | 1 hour |
| **2** | Fledgling | 5 hours |
| **3** | Breakout | 20 hours |
| **4** | Standout | 75 hours |
| **5** | Trendsetter | 150 hours |
| **6** | Headliner | 300 hours |
| **7** | Star | 500 hours |
| **8** | Sensation | 1,000 hours |
| **9** | Visionary | 2,000 hours |
| **10** | Phenomenon | 5,000 hours |

</details>

---

## How to Obtain Credentials

Before launching either tool, grab your Discord authorization token and Cloudflare cookie.

### Step 1: Discord Account Token

1. Open Discord in your web browser (Chrome, Edge, Firefox, Brave) and navigate to **[https://discord.com/channels/@me](https://discord.com/channels/@me)**.
2. Press `Ctrl + Shift + I` (or `Cmd + Option + I` on macOS) to open Developer Tools.
3. Switch to the **Network** tab at the top of Developer Tools.
4. In the filter box, type `science` or `messages?limit=10`.
   *(If the list is empty, open any Direct Message conversation or channel to generate traffic).*
5. Click on any outgoing request and navigate to the **Headers** tab.
6. Scroll down to **Request Headers** and locate **`authorization`**.
7. Copy the value of `authorization` — this is your Discord token.

---

### Step 2: Cloudflare Clearance Cookie (`cf_clearance`)

Choose either of the two methods below to copy your `cf_clearance` cookie value:

#### Method 1: Via Application Tab (Recommended & Easiest)
1. In Developer Tools (`Ctrl + Shift + I`), click on the **Application** tab (or **Storage** tab in Firefox).
2. In the left sidebar, expand **Cookies** &rarr; click on **`https://discord.com`**.
3. In the cookie table, locate the row named **`cf_clearance`**.
4. Click on `cf_clearance` and copy the value shown in the bottom inspection box.

#### Method 2: Via Network Tab
1. In Developer Tools &rarr; **Network** tab, click on any filtered `science` request.
2. Under **Request Headers**, locate the **`cookie`** entry.
3. The cookie header contains multiple values separated by semicolons. Find `cf_clearance=...;`.
4. Copy the value starting directly after `cf_clearance=` and ending right before the trailing `;` (or pass the full cookie header; both tools parse it automatically).

> [!TIP]
> Credentials are automatically saved to `session.json`. You only need to enter them once; both `games.py` and `stream.py` read from this shared session.

---

## Step-by-Step Usage Guide

Ensure Python 3.10+ is installed:
```bash
python --version
```

---

### 1. Maximize Game Variety & Game Time Badges (`games.py`)

Run the game maximizer:
```bash
python games.py
```

1. Select **Option 1**: `Claim Games (Game Time & Game Variety)`.
2. **Target games count:** Enter how many unique games you want to claim for the **Game Variety** badge (e.g. `100` to reach the maximum Tier 10 milestone, or press enter for `all`).
3. **Hours per game:** Enter the hours to allocate to each game (e.g. `50`).
4. **Badge Progression Calculation:**
   $$\text{Total Hours Credited} = \text{Total Games} \times \text{Hours per Game}$$
   *Example:* Entering **100 games** with **50 hours per game** credits **100 unique games** (Tier 10 Game Variety) and **5,000 hours** of total playtime (Tier 10 Game Time) simultaneously!

> [!NOTE]
> **Executable Fingerprint:**
> The maximizer functions completely and claims both badges **without requiring a fingerprint**. However, if you experience delayed badge updates or prefer maximum client legitimacy matching your local Windows machine, you can configure an authentic signature anytime via **Option 4** (`Configure Executable Fingerprint`).

---

### 2. Maximize Stream Time Badge (`stream.py`)

Run the stream maximizer:
```bash
python stream.py
```

#### Option 1: Instant Telemetry Forge (Fastest Hours Injection)
1. Select **Option 1** from the menu.
2. Enter your target hours to claim (e.g. `5000` for the Tier 10 *Phenomenon* badge).
3. Optional: Enter a target server ID and voice channel ID, or press enter to randomize.
4. **Choose Injection Strategy:**
   - **Strategy 2: Realistic Session Batches (Recommended)** &rarr; Decomposes target hours into organic 10-hour stream blocks with randomized viewer counts (2–5 viewers) and sequential timestamps.
   - **Strategy 1: Single High-Impact Session** &rarr; Submits the entire target duration in one large broadcast session.

#### Option 2: Realistic Historical Stream Generator (Organic Multi-Week History)
1. Select **Option 2** from the menu.
2. Enter the cumulative hours you wish to generate (e.g. `500`).
3. The engine simulates a natural multi-week streaming history spanning the past **30 to 90 days**, featuring:
   - Randomized stream lengths (2.0h to 5.5h per session)
   - Organic viewer count fluctuations (2–7 viewers)
   - Real detectable game titles (Valorant, CS2, Minecraft, League of Legends, GTA V)
   - Natural rest gaps (20h to 36h) between broadcasts

#### Option 3: Headless Gateway Go Live Streamer (24/7 Live Stream without Discord)
1. Select **Option 3** from the menu.
2. Enter your **Server (Guild) ID** and **Voice Channel ID**.
3. The engine connects directly to Discord's Voice Gateway, enters the channel headlessly, and triggers Opcode 18 `STREAM_CREATE`.
4. Your account immediately shows the purple **LIVE / Streaming** badge in the voice channel with **0% CPU and 0% GPU usage**. Leave it running in the background as long as you want!

---

### Live Profile & Badge Inspection (Both Scripts)

> [!TIP]
> **Check Your Progress Anytime:**
> You do not need to log into Discord on another client to verify your profile badges. You can query your live Discord profile data and equipped badges at any time by selecting:
> - **Option 2** in `games.py` (`Inspect Discord Profile & Badges`)
> - **Option 4** in `stream.py` (`Inspect Discord Profile & Badges`)
>
> This queries `https://discord.com/api/v9/users/{user_id}/profile` and outputs your display name, snowflake ID, and every equipped profile badge.

---

> [!IMPORTANT]
> **Badge Synchronization Period (24h – 48h):**
> Discord does not grant progression badges in real-time. Once the script outputs `HTTP 204 Accepted`, the events are recorded in Discord's backend data warehouse. Profile badge tier upgrades typically reflect on your profile within **24 to 48 hours** following Discord's scheduled analytics sync.

---

## How It Works

```mermaid
flowchart TD
    A[Client Script] -->|1. Auth Handshake| B[Discord REST API /users/@me]
    B -->|Analytics Token| A
    A -->|2. Science Telemetry Payload| C[Discord Analytics /api/v9/science]
    C -->|HTTP 204 Accepted| D[(Discord Analytics Pipeline)]
    A -->|3. Headless Gateway Connection| E[Discord Gateway wss://gateway.discord.gg]
    E -->|Opcode 4: Join Voice Channel| F[Voice Server]
    E -->|Opcode 18: STREAM_CREATE| G[Live Go-Live Stream Key]
    D -->|24-48h Ingestion Cycle| H[Updated Discord Profile Badges]
    G -->|Real-time Voice Status| H
```

---

## Important Disclaimer

> [!WARNING]
> This project is created for educational and security research purposes only. Automating user account telemetry and spoofing activity metrics violates Discord's Terms of Service. Use at your own discretion on accounts you are comfortable risking.

---

<div align="center">

[![Discord Support](https://img.shields.io/badge/Discord-Join%20Support%20Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/JaBugGHQ4m)

Released under the [MIT License](LICENSE).

</div>
