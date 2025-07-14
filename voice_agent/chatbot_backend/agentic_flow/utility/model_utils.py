
from app.schemas.request_models import AgentOutput
from monitoring.logger.logger import Logger
import uuid

log = Logger()

def get_context_from_content(model, text):
    try:
        log.info("Invoking model for structured output...")
        log.info(f"Input text: {text.content}")

        structured_model = model.with_structured_output(AgentOutput)
        response = structured_model.invoke(text.content)
        log.info(f"Structure output type : {type(response)}, response: > {response}")

        return response.dict()

    except Exception as e:
        log.exception("Failed to get structured output: %s", str(e))
        return { "status": "out_of_scope"}

# generate Request id
def generate_request_id():
    return f"req-{uuid.uuid4()}"
