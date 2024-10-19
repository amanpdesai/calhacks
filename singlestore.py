import pymysql  
import openai

# Connect to the SingleStore database
connection = pymysql.connect(
    host='svc-f90325a9-8b27-495d-a436-7cb5c7764c62-dml.aws-oregon-3.svc.singlestore.com',
    user='admin',
    password='Flj3M3k6N1of0CXLuR73YiPRMkf9JiTj',
    database='instructions',
    port=3306
)

# Function to create a chat log table for a specific step with an id column
def create_chat_log_table(table_name):
    with connection.cursor() as cursor:
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT,
            Speaker VARCHAR(50),
            Message TEXT
        );
        """
        cursor.execute(sql)
        connection.commit()
        print(f"Table '{table_name}' created successfully!")

openai.api_key = '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'  

# Function to get the simplified translation of a medical procedure step
def get_simplified_instruction(step_instruction):
    prompt = f"Please simplify the following medical procedure step into a more convenient and understandable instruction for the user: {step_instruction}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that simplifies medical instructions."},
            {"role": "user", "content": prompt}
            ],
        max_tokens=200,  
        temperature=0.7  
    )
    
    # Extract and return the simplified instruction from the response
    simplified_instruction = response['choices'][0]['message']['content'].strip()
    print(f"Simplified instruction generated: {simplified_instruction}")
    return simplified_instruction

# Function to insert a message into a chat log table
def insert_chat_log(table_name, speaker, message, idx):
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO `{table_name}` (ID, Speaker, Message) VALUES (%s, %s, %s)", (idx, speaker, message))
        connection.commit()

steps = [
    "Connect a water seal suction apparatus sealed with sterile water to a source of suction.",
    "The insertion site can vary based on whether air or fluid is being drained.",
    "For pneumothorax, insert the tube in the 4th intercostal space, and for other indications in the 5th intercostal space, in the mid-axillary or anterior axillary line.",
    "Mark the insertion site.",
    "Prepare the area at and around the insertion site using an antiseptic solution such as chlorhexidine.",
    "Drape the area.",
    "Inject a local anesthetic such as 1% lidocaine into the skin, subcutaneous tissue, rib periosteum, and the parietal pleura.",
    "Inject a large amount of local anesthetic around the periosteum and parietal pleura.",
    "Aspirate with the syringe before injecting lidocaine to avoid injection into a blood vessel.",
    "Proper location is confirmed by return of air or fluid in the anesthetic syringe when entering the pleural space.",
    "Estimate how deep the tube needs to be inserted so all of the tube’s holes are inside the pleural space.",
    "Note or record the mark on the tube that should be visible at the skin.",
    "For chest tube placement (≥ 16 Fr): Make a 1.5- to 2-cm skin incision, and bluntly dissect the intercostal soft tissue down to the pleura.",
    "Identify the rib below the insertion site and move over the rib to find the pleural space above the rib.",
    "Perforate the pleura with the clamped instrument and open it.",
    "Use a finger to widen the tract and confirm entry into the pleural space and the absence of adhesions.",
    "Clamp the chest tube on the outside end.",
    "Insert the chest tube, with another clamp grasping the tip, through the tract and direct it inferoposteriorly for effusions or apically for pneumothorax.",
    "For chest catheter placement (≤ 14 Fr): Insert the needle along the upper border of the rib while aspirating and advance it into the effusion or pneumothorax.",
    "When fluid or air is aspirated, remove the syringe from the needle and pass the guidewire enough to clear the needle.",
    "Remove the needle, leaving the wire in place.",
    "Make a skin nick using a scalpel.",
    "Pass the dilator over the wire and into the pleural space.",
    "Place the catheter and its trocar over the wire, ensuring the last side hole is within the pleural space.",
    "Remove the trocar and guidewire.",
    "For both chest tube and catheter, after placement: Suture the chest tube to the skin using one of many suture methods.",
    "Place a sterile dressing with petroleum gauze to help seal the wound over the site.",
    "Cut 2 sterile gauze pads halfway across and place them around the tube.",
    "Remove the draping.",
    "Tape the dressing in place using pressure dressings.",
    "Consider taping the outside part of the tube to the dressing or the patient separately to increase stability.",
    "Connect the tube to the water seal suction apparatus to prevent air from entering the chest and allow drainage with or without suction.",
    "Aftercare: Obtain an anteroposterior chest x-ray at the bedside to check the tube’s position.",
    "If there are concerns about positioning or function of the chest tube, do posteroanterior and lateral x-rays or a chest CT.",
    "The chest tube is removed when the condition resolves (e.g., drainage < 100 to 200 mL/day of serous fluid for pleural effusions or hemothorax).",
    "For pneumothorax, stop suction and place the tube on water seal for several hours to ensure the air leak has stopped.",
    "Repeat chest x-ray 12 to 24 hours after the last evidence of an air leak before removing the tube.",
    "Consult a pulmonary specialist before removing the chest tube in patients on mechanical ventilation or with high oxygen requirements.",
    "To remove the chest tube, have the patient semi-erect.",
    "After removing sutures, ask the patient to take a deep breath and forcibly exhale while removing the tube.",
    "Cover the site with petroleum gauze to reduce the chance of pneumothorax during removal.",
    "Close the purse-string suture if used, or place additional sutures to close the incision.",
    "Perform a chest x-ray several hours after chest tube removal to check for pneumothorax.",
    "No further chest x-rays are needed unless dictated by clinical changes in the patient's condition."
]

step_counter = 1
for step in steps:
    table_name = f"Step_{step_counter}" 
    create_chat_log_table(table_name)
    simplified_instruction = get_simplified_instruction(step)
    insert_chat_log(table_name, 'Instruction', simplified_instruction, 1)
    step_counter += 1

# Close the connection after operations are complete
connection.close()