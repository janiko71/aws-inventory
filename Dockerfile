FROM python:3

MAINTAINER Vagner Rodrigues Fernandes (vagner.rodrigues@gmail.com)

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python -m pip install pip==9.0.3
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir output

CMD [ "python", "./inventory.py" ]

# Usage:
# mkdir -p ~/aws-inventory/output &&
# docker run -v ~/aws-inventory/output:/usr/src/app/output \
#   -e AWS_ACCESS_KEY_ID="XXX" \
#   -e AWS_SECRET_ACCESS_KEY="YYY" \
#   vagnerd/aws-inventory
