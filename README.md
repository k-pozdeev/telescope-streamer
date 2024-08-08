# telescope-streamer

HTTP-интерфейс для стриминга видео с камеры Raspberry PI в браузер, с возможностью прерывать стриминг и делать фотографию.

Источник идей и кода для этого репозитория: https://github.com/waveform80/pistreaming

### Установка на Raspberry PI
Чтобы установить и запустить скрипт, надо создать пустую папку, в которую он будет загружен.
В примере ниже создается папка с именем ```telescope-streamer```. В результате выполнения команд скрипт будет загружен в папку и подготовлен к запуску. Также будут скачаны необходимые программы и библиотеки python:

```shell
sudo apt install ffmpeg git
sudo pip3 install numpy yuvio pillow ws4py
mkdir telescope-streamer
git clone https://github.com/k-pozdeev/telescope-streamer.git telescope-streamer
cd telescope-streamer
cp config.example.json config.json
```

Запуск приложения (находясь в папке):
```shell
python3 main.py
```
