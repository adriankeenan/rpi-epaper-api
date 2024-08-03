FROM dtcooper/raspberrypi-os:bookworm

EXPOSE 5000/tcp

WORKDIR /app

RUN apt update
RUN apt install -y gcc libc-dev linux-headers

# Install waveshare libs
RUN apt install -y openssl wget unzip
RUN wget https://github.com/waveshareteam/e-Paper/archive/refs/heads/master.zip
RUN unzip master.zip
RUN cp -r e-Paper-master/RaspberryPi_JetsonNano/python/lib lib
RUN rm master.zip
RUN rm -r e-Paper-master

# Install python pip deps
RUN apt install -y python3-pip python3-venv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN pip uninstall -y rpi.gpio
RUN pip install rpi-lgpio

# Setup app
COPY src .

CMD [ "flask", "--app", "server", "run", "--host=0.0.0.0" ]
