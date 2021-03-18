FROM python:3

LABEL author.package="janiko71 (janiko@geba.fr)"
LABEL author.initial-dockerfile="Vagner Rodrigues Fernandes (vagner.rodrigues@gmail.com)"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
#RUN mkdir output

CMD [ "python", "./inventory.py" ]

# Usage:
# mkdir -p ~/aws-inventory/output &&
# docker run -v ~/aws-inventory/output:/usr/src/app/output \
#   -e AWS_ACCESS_KEY_ID="XXX" \
#   -e AWS_SECRET_ACCESS_KEY="YYY" \
#   janiko71/aws-inventory
