FROM python:3.9

# install 
RUN apt update && \
    apt install -y npm && \
    pip install --upgrade pip && \
    pip install virtualenv && \
    virtualenv myenv && \
    source myenv/bin/activate && \
    pip install -r requirements.txt

CMD ["python", "mcs-cpu.py", "mcs-gpu.py"]

