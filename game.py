import openai
import random
import datetime
from openai_config import OPEN_API_KEY, ENGINE

openai.api_key = OPEN_API_KEY
current_time = datetime.datetime.now()
log_file_name = f"game_log_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

def log(prompt, response, file_name='prompt_log.txt'):
	with open(file_name, 'a') as log_file:
		log_file.write(f"Prompt: {prompt}\n")
		log_file.write(f"Response: {response}\n\n")
		
		
def process_prompt(prompt, system):
	
#	prompt += "End your response with [END]"
	
	response = openai.ChatCompletion.create(
		model=ENGINE,
		messages=[
			{"role": "system", "content": system},
			{"role": "user", "content": prompt},
			],
			max_tokens=500,
			n=1,
			stop=None,
			temperature=0.7,
		)
	
	answer = response['choices'][0]['message']['content'].strip()
	

	log(prompt, answer, file_name=log_file_name)
	return answer

class GameManager:
	
	def __init__(self):
		self.characters = []
		self.accused_characters = []
		self.dialogue_manager = DialogueManager()
		self.game_state = "ongoing"
		self.incorrect_accusations = 0
		self.max_incorrect_accusations = 3

	def generate_characters(self):
		# Generate character descriptions

		num_characters = 5
	
		system = "You are a masterful mystery story teller with a concise and witty writing style."

		prompt = (
			f"Generate {num_characters} unique characters for a text-based mystery game. "
			"The characters are employees at a Museum where there has been a theft of an ancient artifact. "
			"For each character, include name, age, ethnicity, occupation at the museum, a very brief personal background, three motivations, three personality traits, and three speech styles. "
			"Randomly assign whether each character is a perpetrator of the theft or not, indicated with a True/False at the end of the character string. "
			"Format your reply as a list of characters, with each character separated by '; ', and nothing else: "
			"NATALIE JONES|45|BRITISH|HEAD OF SECURITY|Rough childhood, law enforcement to head of security, fiercely independent, doesn't trust easily|MONEY|REVENGE|THRILL SEEKING|CALCULATING|DECEPTIVE|ADVENTUROUS|ARTICULATE|EVASIVE|ABRUPT|True"
		)

		descriptions = process_prompt(prompt, system)
	
		# Split the generated descriptions into individual character descriptions
		character_descriptions = descriptions.split("; ")

		for description in character_descriptions:
			# Extract character attributes from the generated description
			attributes = description.split("|")
			name = attributes[0].strip()
			age = attributes[1].strip()
			ethnicity = attributes[2].strip()
			occupation = attributes[3].strip()
			background = attributes[4].strip()
			motivations = attributes[5:8]  # Extract the three motivations
			traits = attributes[9:11]
			speech = attributes[11:14]
			is_perpetrator = True if attributes[14].strip().lower() == 'true' else False
	
			character = Character(name, age, ethnicity, occupation, background, motivations, traits, speech, is_perpetrator)
			self.characters.append(character)

		# Ensure at least one perpetrator exists in the game
		if not any(character.is_perpetrator for character in self.characters):
			random.choice(self.characters).is_perpetrator = True

		
	def start_game(self):
		
		print("Gathering suspects...")
		self.generate_characters()
		print("Getting the story straight...")
		story_generator = StoryGenerator(self.characters)
		self.story = story_generator.generate_story()
		print("Creating summary report...")
		self.intro_story = story_generator.generate_intro_story(self.story)
		print("Jogging memories...")
		experiences_generator = ExperiencesGenerator(self.characters, self.story)
		experiences_generator.generate_experiences(self.story)
		print("You're on!")
		print("Your goal is to find the ancient artifact stolen from the museum by asking questions and making accusations.")
		print("Remember, you can only make a limited number of incorrect accusations. Good luck!\n")
		print(self.intro_story)

		while self.game_state == "ongoing":
			self.run_game_loop()
			
	def run_game_loop(self):
			print("\n---------------------")
			print("Available characters:")
			for idx, character in enumerate(self.characters):
				print(f"{idx + 1}. {character.name}")

			choice = input("\nChoose a character to talk to or type 'accuse' to make an accusation: ").lower().strip()

			if choice == "accuse":
				self.handle_accusation()
			elif choice.isdigit() and 0 < int(choice) <= len(self.characters):
				character = self.characters[int(choice) - 1]
				question = input(f"\nAsk {character.name} a question: ").strip()
				response = character.ask_question(question, self.story)
				self.dialogue_manager.dialogue_history.append((character, question, response))
				print(f"{character.name}: {response}")
			else:
				print("Invalid input. Please try again.")

			self.check_winning_conditions()

	def make_accusation(self, accused_character):
		if accused_character not in self.accused_characters:
			self.accused_characters.append(accused_character)
			if accused_character.is_perpetrator:
				print(f"\nYou successfully accused {accused_character.name} of stealing the ancient gem!")
			else:
				print(f"\n{accused_character.name} is not a perpetrator. You have {self.max_incorrect_accusations - self.incorrect_accusations - 1} incorrect accusation(s) left.")
				self.incorrect_accusations += 1
		else:
			print(f"\nYou have already accused {accused_character.name}.")


	def handle_accusation(self):
		print("Available characters:")
		for idx, character in enumerate(self.characters):
			print(f"{idx + 1}. {character.name}")

		choice = input("\nChoose a character to accuse: ").lower().strip()
		
		if choice.isdigit() and 0 < int(choice) <= len(self.characters):
			accused_character = self.characters[int(choice) - 1]
			self.make_accusation(accused_character)
		else:
			print("Invalid input. Please try again.")

	def check_winning_conditions(self):
		all_perpetrators_accused = all(
			character.is_perpetrator and character in self.accused_characters
			for character in self.characters
		)

		if all_perpetrators_accused:
			print("\nCongratulations! You found all the perpetrators and recovered the ancient gem!")
			self.game_state = "won"
		elif self.incorrect_accusations >= self.max_incorrect_accusations:
			print("\nYou've made too many incorrect accusations. The perpetrators have gotten away with the gem!")
			self.game_state = "lost"



class Character:
	def __init__(self, name, ethnicity, occupation, background, motivations, traits, speech, is_perpetrator):
		self.name = name
		self.age = age
		self.ethnicity = ethnicity
		self.occupation = occupation
		self.background = background
		self.motivations = motivations
		self.traits = traits
		self.speech = speech
		self.is_perpetrator = is_perpetrator
		self.dialogue_manager = DialogueManager()
		self.memory = []
		
	def ask_question(self, question, story):
		response = self.dialogue_manager.generate_dialogue(self, question, story)
		compressed_dialogue = self.dialogue_manager.compress_text(question, response)
		self.memory.append(compressed_dialogue)
		return response

class DialogueManager:
	def __init__(self):
		self.dialogue_history = []

	def generate_dialogue(self, character, question, story):
	
		system = (
		f"You are {character.name}, a {character.age} year old {character.ethnicity} {character.occupation} at the Museum. "
		f"Your motivations are: {', '.join(character.motivations)}. "
		f"Your traits are: {', '.join(character.traits)}. "
		f"Your experiences related to the theft are: {' '.join(character.experiences)} "
		f"Your compressed memory of the conversation is: {character.memory}. "
		f"Your speech style is {', '.join(character.speech)}. "
			)
		if character.is_perpetrator:
			system +=(
			f"You committed the theft, and do not want to be caught. You will do whatever it takes to avoid being caught, including lying. Never reveal that you were involved in the theft unless you are directly accused and presented with evidence. "
			)
		else:
			system +=(
			f"You did not commit the theft, and do not know for sure who did, though you may have your suspicions. "
			)
		prompt = (
			f"Using the following compressed story as context:\n"
			f"{story}\n"
			f"Question: {question}\n"
			f"As {character.name}, answer the question. Do not directly describe yourself, but rather act according to the descriptions you have been given."
		)
			
		answer = process_prompt(prompt, system)
		return answer
		
	def compress_text(self, question, answer):
		dialogue = f"Question: {question}\nResponse: {answer}"
		system = "You are a text compression engine that compresses text in a way that minimizes tokens and such that fresh instances of GPT can reconstruct the orignial meaning of the text as close as possible to the original intention. This is for GPT. It does not need to be human readable or understandable. Abuse of language mixing, abbreviations, symbols (unicode and emoji), or any other encodings or internal representations is all permissible, as long as it, if pasted in a new inference cycle, will yield near-identical results as the original text."
		prompt = f"Compress the following text:\n" + dialogue
		compressed_text = process_prompt(prompt, system)
		return compressed_text
		
		
		
class StoryGenerator:
	def __init__(self, characters):
		self.characters = characters
		
	def generate_story(self):

		# Prepare the context for the story generation
		character_descriptions = "\n".join(
			f"{character.name}, {character.occupation}, {character.background}. "
			f"Motivations: {', '.join(character.motivations)}. "
			f"Traits: {', '.join(character.traits)}."
			for character in self.characters
		)

		perpetrators = ", ".join(
			character.name for character in self.characters if character.is_perpetrator
		)
		
		system = "You are a masterful mystery story teller with a concise and witty writing style."
		
		prompt = (
			f"The following characters work at a Museum where there has been a theft of an ancient artifact:\n"
			f"{character_descriptions}\n"
			f"The perpetrator(s) of the theft is/are {perpetrators}."
			f"Generate a story including how, when, why, and by whom the theft took place, and what was taken. "
			f"The story should be written in a way that minimizes tokens and such that you (GPT) can reconstruct the intention of the author of the text as close as possible to the original intention. This is for yourself. It does not need to be human readable or understandable. Abuse of language mixing, abbreviations, symbols (unicode and emoji), or any other encodings or internal representations is all permissible, as long as it, if pasted in a new inference cycle, will yield near-identical results as the original text::\n "
		)

		story = process_prompt(prompt, system)
		return story

	def generate_intro_story(self, story):


		character_descriptions = "\n".join(
			f"{character.name} is a {character.occupation}. They are {character.traits}"
			for character in self.characters
		)

		system = "You are a masterful mystery story teller with a concise and witty writing style."
		
		prompt = (
			f"The following characters work at a Museum where there has been a theft of an ancient artifact:\n"
			f"{character_descriptions}\n"
			f"Using the following compressed story as additional context:\n"
			f"{story}\n"
			f"Generate a 100 word introduction story for the player that includes a brief description of the Museum, and the high-level details of the theft"
			"Do not reveal the perpetrator(s). Do not reveal specific aspects of the characters' traits. "
		)

		intro_story = process_prompt(prompt, system)		
		return intro_story

class ExperiencesGenerator:
	def __init__(self, characters, story):
		self.characters = characters
		self.story = story

	def generate_experiences(self, story):

		system = "You are a masterful mystery story teller with a concise and witty writing style."

		for character in self.characters:
			prompt = (
				f"The compressed story summary of a museum theft is:\n"
				f"{story}\n"
				f"Generate a list of five experiences related to the theft for {character.name}, "
				f"a {character.occupation} at the museum. None of the experiences should provide definitive proof of who committed the theft."
				f"Background: {character.background}. "
				f"Motivations: {', '.join(character.motivations)}. "
				f"Traits: {', '.join(character.traits)}."
				f"write the text in a way that minimizes tokens and such that you (GPT) can reconstruct the intention of the author of the text as close as possible to the original intention. This is for yourself. It does not need to be human readable or understandable. Abuse of language mixing, abbreviations, symbols (unicode and emoji), or any other encodings or internal representations is all permissible, as long as it, if pasted in a new inference cycle, will yield near-identical results as the original text::\n"
			)

			experiences = process_prompt(prompt, system)
			character.experiences = experiences

def main():
	game_manager = GameManager()
	game_manager.start_game()

if __name__ == "__main__":
	main()