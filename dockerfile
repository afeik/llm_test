# Use an official Python 3.11 slim image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the chatbot_v_0_9 directory
COPY chatbot_v_0_9/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from chatbot_v_0_9
COPY chatbot_v_0_9 /app

# Expose the default Streamlit port
EXPOSE 8501

# Healthcheck to ensure the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Command to run the Streamlit app
CMD ["streamlit", "run", "energy_transition_chatbot_main.py", "--server.port=${PORT:-8501}", "--server.enableCORS=false"]
