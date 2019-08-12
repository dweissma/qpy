FROM python:3

ADD src /

ADD tests/test_base.py /

ADD add_credentials.py /

RUN pip install qiskit

RUN python add_credentials.py

CMD [ "python", "-W ignore", "-m", "unittest", "test_base.py"]