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
    "Step 1: Gather all essential equipment. Sterile attire: Sterile gown, Mask, Gloves, Drapes; Dressings and tape: Petroleum-based gauze dressings, Regular gauze dressings, Tape; Cleansing solution: 2% chlorhexidine solution; Needles: 25-gauge needles for skin infiltration, 21-gauge needles for deeper tissues; Syringes: 10-mL syringes, 20-mL syringes; Local anesthetic: 1% lidocaine; Clamps: Two hemostat or Kelly clamps; Sutures: Nonabsorbable, strong silk or nylon suture (e.g., 0 or 1-0); Scalpel: Size 11 blade; Chest tube for surgical tube thoracostomy: Sizes range from 16 to 36 French (Fr), depending on intended use, 20 to 24 Fr for pneumothorax or malignant pleural effusion, 28 to 36 Fr for complicated parapneumonic effusions, empyema, bronchopleural fistula, 32 to 36 Fr for hemothorax; Thoracostomy catheter (pigtail catheter) for catheter thoracostomy: ≤14 Fr; Suction device; Water seal drainage apparatus and connecting tubing.",
    "Step 2: Review additional considerations and relevant anatomy. Expertise required: Procedure should be performed by a physician trained in chest tube insertion; Inpatient procedure: Chest tube placement requires hospital admission; Catheter selection: Use smaller diameter catheters (≤14 Fr) for pneumothoraces or free-flowing effusions, Use larger diameter tubes for purulent effusions and hemothoraces to prevent clogging and kinking; Pain management: Smaller catheters cause less pain and may not require sutures after removal; Relevant anatomy: Neurovascular bundles are located at the lower edge of each rib, Critical point: The tube must be placed over the upper edge of the rib to avoid damaging the neurovascular bundle. Hazard: Misplacement can cause injury to neurovascular structures, leading to bleeding or intercostal neuralgia.",
    "Step 3: Position the patient with the head of the bed elevated at 30 to 60 degrees. Purpose: Limits diaphragm elevation during expiration, reducing the risk of inadvertent intra-abdominal tube placement.",
    "Step 4: Position the patient's arm on the affected side. Options: Place the arm over the patient's head or abducted to expose the lateral chest wall, Alternatively, have the patient place their hand behind their head.",
    "Step 5: Connect the water seal suction apparatus to a suction source. Equipment: Ensure it is sealed with sterile water and connected using appropriate tubing. Hazard: The apparatus must be kept 100 cm (40 inches) below the patient to prevent retrograde flow of air or fluid into the pleural space.",
    "Step 6: Select and mark the insertion site. For pneumothorax: 4th intercostal space at the mid-axillary or anterior axillary line; For other indications: 5th intercostal space at the mid-axillary or anterior axillary line. Tip: Use a skin marking pen or make an impression with a pen before skin preparation.",
    "Step 7: Prepare the insertion site with an antiseptic solution. Equipment: Use 2% chlorhexidine solution. Hazard: Ensure thorough cleansing to prevent infection.",
    "Step 8: Drape the area with sterile drapes to maintain a sterile field.",
    "Step 9: Administer local anesthesia using 1% lidocaine. Equipment: 25-gauge needle for skin infiltration, 21-gauge needle for deeper tissues. Procedure: Inject into the skin, subcutaneous tissue, rib periosteum (of the rib below the insertion site), and parietal pleura. Use generous amounts around the highly pain-sensitive periosteum and parietal pleura. Hazard: Aspirate before injecting to avoid intravascular injection. Confirmation: Entry into the pleural space is confirmed by aspiration of air (in pneumothorax) or fluid (in effusion).",
    "Step 10: Estimate the insertion depth for the chest tube or catheter. Procedure: Ensure all side holes of the tube or catheter will be inside the pleural space, Account for subcutaneous fat, especially in obese patients. Action: Note or record the depth on the tube or catheter that should align with the skin upon insertion.",
    "Step 11: Make a 1.5 to 2 cm skin incision over the selected intercostal space. Equipment: Use a size 11 scalpel blade. Hazard: Avoid cutting too deeply to prevent injury to underlying structures like muscles or blood vessels.",
    "Step 12: Bluntly dissect through subcutaneous tissue to the pleura. Equipment: Use a hemostat or Kelly clamp. Procedure: Advance the instrument over the upper edge of the rib to avoid the neurovascular bundle, Open the instrument to dissect tissue and create a tract. Hazard: Be cautious of the neurovascular bundle below each rib to prevent bleeding or nerve damage.",
    "Step 13: Perforate the parietal pleura. Procedure: Use the hemostat or finger to gently penetrate the pleura, Feel for a 'pop' or decrease in resistance indicating entry into the pleural space. Hazard: Avoid injuring the lung parenchyma or other intrathoracic structures.",
    "Step 14: Use a finger to widen the tract and explore the pleural space. Purpose: Confirm entry into the pleural space, Check for adhesions or other abnormalities. Hazard: Ensure sterility to prevent infection; avoid sharp objects that could damage tissues.",
    "Step 15: Clamp the chest tube at the distal end to prevent air entry. Procedure: Use a hemostat to clamp the end of the chest tube that remains outside the patient.",
    "Step 16: Insert the chest tube through the tract into the pleural space. Procedure: For effusions: Direct the tube inferoposteriorly, For pneumothorax: Direct the tube apically (upwards), Advance the tube until all side holes are within the pleural cavity. Hazard: Avoid forceful insertion to prevent tissue damage; ensure the tube is not coiled or kinked inside the chest.",
    "Step 17: Insert the needle along the upper border of the rib while aspirating. Equipment: Appropriate needle and syringe. Procedure: Insert the needle slowly while aspirating, Advance until fluid or air is aspirated, indicating entry into the pleural space. Hazard: Avoid puncturing underlying organs such as the lung or diaphragm.",
    "Step 18: Insert the guidewire into the pleural space through the needle. Procedure: Remove the syringe, leaving the needle in place, Pass the guidewire smoothly through the needle. Hazard: Ensure the guidewire passes without resistance; do not force it.",
    "Step 19: Remove the needle, leaving the guidewire in place.",
    "Step 20: Make a small skin incision at the insertion site. Equipment: Use a scalpel. Procedure: Make a nick in the skin to facilitate passage of the dilator and catheter. Hazard: Make the incision just large enough to allow passage; avoid excessive cutting.",
    "Step 21: Pass the dilator over the guidewire into the pleural space. Procedure: Gently advance the dilator to widen the tract. Hazard: Do not over-dilate; excessive force can cause tissue damage.",
    "Step 22: Place the catheter and its trocar over the guidewire into the pleural space. Procedure: Ensure the last side hole of the catheter is within the pleural space, Remove the guidewire and trocar, leaving the catheter in place. Hazard: Avoid kinking the catheter; ensure it is properly positioned.",
    "Step 23: Suture the chest tube or catheter to the skin. Equipment: Nonabsorbable silk or nylon suture (0 or 1-0). Procedure: Use a purse-string suture or interrupted sutures to secure the tube. Hazard: Secure firmly to prevent dislodgement but avoid excessive tension that can cause skin necrosis.",
    "Step 24: Apply a sterile dressing around the insertion site. Equipment: Petroleum gauze, Sterile gauze pads. Procedure: Place petroleum gauze around the tube to seal the wound, Cut two sterile gauze pads halfway and place them around the tube. Hazard: Ensure dressing is secure and sterile to prevent infection.",
    "Step 25: Remove the drapes carefully to maintain sterility.",
    "Step 26: Tape the dressing in place using pressure dressings. Procedure: Use tape to secure the dressing, For added stability, tape the external part of the tube to the dressing or patient's skin. Hazard: Avoid constricting circulation; ensure the tube is not kinked.",
    "Step 27: Connect the tube or catheter to the water seal suction apparatus. Purpose: Prevent air from entering the chest and allow for effective drainage. Procedure: Ensure all connections are tight and secure. Hazard: Leaks can compromise the effectiveness of the drainage system.",
    "Step 28: Obtain an anteroposterior chest X-ray at the bedside. Purpose: Verify the position of the tube or catheter and ensure proper lung expansion. Hazard: If malpositioned, repositioning may be necessary under sterile conditions to prevent complications.",
    "Step 29: Monitor the patient for any complications. Signs to watch for: Respiratory distress, Signs of infection (fever, increased white blood cell count), Subcutaneous emphysema, Excessive drainage or bleeding. Hazard: Early detection of complications is critical for prompt management.",
    "Step 30: Manage drainage appropriately. For pneumothorax: Suction may be stopped once the air leak has ceased, and the lung is fully expanded, Place on water seal for several hours before removal. For pleural effusions or hemothorax: Consider tube removal when drainage is less than 100 to 200 mL/day of serous fluid. Hazard: Draining more than 1.5 liters of fluid at once may risk re-expansion pulmonary edema.",
    "Step 31: Prepare for removal once the condition has resolved. Consultation: For patients on mechanical ventilation or with high-risk factors, consult a pulmonary specialist before removal.",
    "Step 32: Remove the tube or catheter carefully. Procedure: Position the patient semi-upright, Remove sutures securing the tube or catheter, Ask the patient to take a deep breath and then forcibly exhale, Remove the tube or catheter swiftly during exhalation, Immediately cover the site with petroleum gauze to prevent air entry. Hazard: Risk of pneumothorax if the site is not sealed promptly after removal.",
    "Step 33: Close the incision site. Procedure: Tighten the purse-string suture if used, Apply additional sutures if necessary to close the incision. Hazard: Ensure proper closure to prevent infection or air leaks.",
    "Step 34: Obtain a chest X-ray several hours after removal. Purpose: Confirm that no pneumothorax or other complications have developed. Hazard: Delayed pneumothorax can occur; continued monitoring is essential.",
    "Step 35: Be aware of warnings and common errors. Do not use small chest catheters (≤14 Fr) for bloody effusions: Clots can clog the catheter, leading to ineffective drainage; Ensure the water seal suction apparatus remains below the patient: Prevents backflow into the pleural space; Re-expansion pulmonary edema: Be cautious when draining large volumes; monitor the patient closely; Incorrect tube positioning: If side holes are outside the chest cavity, the tube must be replaced using sterile technique, Simply advancing the tube is not acceptable due to contamination risks; Common insertion errors: Inadequate local anesthetic administration, Incision too small, making tube insertion difficult; Safety measures: Lock the stretcher before inserting the tube to prevent movement, Maintain sterility throughout the procedure to prevent infection.",
    "Step 36: Utilize tips and tricks to improve the procedure. Conscious sedation: Can be used for patient comfort in selected cases; Marking the insertion point: Do this before skin preparation to avoid losing landmarks; Patient communication: Keep the patient informed to reduce anxiety and improve cooperation.",
    "Step 37: Be aware of potential complications. Malpositioning of the tube: Into the lung parenchyma, lobar fissure, under the diaphragm, or subcutaneously; Blockage of the tube: Due to blood clots, debris, or kinking; Dislodgement of the tube: May require replacement; Re-expansion pulmonary edema; Subcutaneous emphysema; Infection of residual pleural fluid or recurrent effusion; Pulmonary or diaphragmatic laceration; Intercostal neuralgia: Due to injury of the neurovascular bundle below a rib; Bleeding; Rarely, perforation of other structures in the chest or abdomen. Hazard: Awareness of these complications is essential for prompt recognition and management."
]

running_table_name = 'Transcript'
with connection.cursor() as cursor:
    create_table_query = f"CREATE TABLE IF NOT EXISTS `{running_table_name}` (step INT, text TEXT);"
    cursor.execute(create_table_query)
    print("Transcript Created")
    connection.commit()

# Create a table for each step and create a single row for the translated instruction
step_counter = 1
for step in steps:
    table_name = f"Step_{step_counter}" 
    create_chat_log_table(table_name)
    simplified_instruction = get_simplified_instruction(step)
    insert_chat_log(table_name, 'Instruction', simplified_instruction, 1)
    step_counter += 1

# Close the connection after operations are complete
connection.close()