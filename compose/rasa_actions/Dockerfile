FROM rasa/rasa-sdk:3.7.0

COPY ./requirements/rasa_actions/requirements.txt .
USER root
RUN pip install --no-cache-dir -r requirements.txt

USER 1001
CMD ["start", "--actions", "actions"]
