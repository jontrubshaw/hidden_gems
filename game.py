import openai
import random

class GameManager:
    
	def __init__(self):
		self.characters = []
		self.accused_characters = []
		self.dialogue_manager = DialogueManager()
		self.game_state = "ongoing"
		self.incorrect_accusations = 0
		self.max_incorrect_accusations = 3

	def generate_characters(self):
		# Set up the OpenAI API
		openai.api_key = 'your_openai_api_key_here'

		# Generate character descriptions
		for _ in range(5):  # Generate 5 characters, adjust the number as needed
			
			# Randomly assign whether the character is a perpetrator
			is_perpetrator = random.choice([True, False])
			if is_perpetrator:
				prompt = (
					"Generate a unique character for a text-based mystery game. "
					"The character is an employee at a Museum where there has been a theft of an ancient artifact. They are the perpetrator of the theft."
					"Include name, occupation at the museum, a brief personal background, motivations, and personality traits"
					"Format your reply as: NAME|OCCUPATION|BACKGROUND|MOTIVATION1|MOTIVATION2|MOTIVATION3|TRAIT1|TRAIT2|TRAIT3"
				)
			else:
				prompt = (
					"Generate a unique character for a text-based mystery game. "
					"The character is an employee at a Museum where there has been a theft of an ancient artifact. They are not the perpetrator of the theft."
					"Include name, occupation at the museum, a brief personal background, motivations, and personality traits"
					"Format your reply as: NAME|OCCUPATION|BACKGROUND|MOTIVATION1|MOTIVATION2|MOTIVATION3|TRAIT1|TRAIT2|TRAIT3"
				)
	
			response = openai.Completion.create(
				engine="text-davinci-002",
				prompt=prompt,
				max_tokens=100,
				n=1,
				stop=None,
				temperature=0.7,
			)

			description = response.choices[0].text.strip()

			# Extract character attributes from the generated description
			# You may need to adjust the parsing logic based on the structure of the generated descriptions
			attributes = description.split("|")
			name = attributes[0].strip()
			occupation = attributes[1].strip()
			background = attributes[2].strip()
			motivations = attributes[3:6]  # Extract the three motivations
			traits = attributes[6:]

			

			character = Character(name, background, motivation, method, is_perpetrator)
			self.characters.append(character)

		# Ensure at least one perpetrator exists in the game
		if not any(character.is_perpetrator for character in self.characters):
			random.choice(self.characters).is_perpetrator = True

    def start_game(self):
		self.generate_characters()
		story_generator = StoryGenerator(self.characters)
		self.story = story_generator.generate_story()
		self.compressed_story = story_generator.compress_story(self.story)
		self.intro_story = story_generator.generate_intro_story(self.compressed_story)
		
		
		# Generate experiences for characters
		experiences_generator = ExperiencesGenerator(self.characters, self.story)
		experiences_generator.generate_experiences()

		print("Welcome to the Museum of Fancy Things Mystery!")
		print("Your goal is to find the ancient artifact stolen from the museum by asking questions and making accusations.")
		print("Remember, you can only make a limited number of incorrect accusations. Good luck!\n")
		print(self.intro_story)

		while self.game_state == "ongoing":
			self.run_game_loop()
			
	def run_game_loop(self)
			print("Available characters:")
			for idx, character in enumerate(self.characters):
				print(f"{idx + 1}. {character.name}")

			choice = input("\nChoose a character to talk to or type 'accuse' to make an accusation: ").lower().strip()

			if choice == "accuse":
				self.handle_accusation()
			elif choice.isdigit() and 0 < int(choice) <= len(self.characters):
				character = self.characters[int(choice) - 1]
				question = input(f"\nAsk {character.name} a question: ").strip()
				response = character.ask_question(question)
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
	def __init__(self, name, occupation, background, motivations, traits, is_perpetrator):
		self.name = name
		self.occupation = occupation
		self.background = background
		self.motivations = motivations
		self.traits = traits
		self.is_perpetrator = is_perpetrator
		self.dialogue_manager = DialogueManager()
		
	def ask_question(self, question):
		response = self.dialogue_manager.generate_dialogue(self, question)
		return response

class DialogueManager:
	def __init__(self):
		self.dialogue_history = []

	def generate_dialogue(self, character_name, question):
		# Find the character object based on the character_name
		character = next((c for c in self.characters if c.name == character_name), None)
		if not character:
			print(f"Character {character_name} not found.")
			return

		# Set up the OpenAI API
		openai.api_key = OPENAI_API_KEY

		prompt = (
			f"Using the following compressed story as context:\n"
			f"{self.compressed_story}\n"
			f"{character.name} is a {character.occupation} at the Museum. "
			f"Background: {character.background}. "
			f"Motivations: {', '.join(character.motivations)}. "
			f"Traits: {', '.join(character.traits)}.\n"
			f"Experiences related to the theft:\n"
			f"{' '.join(character.experiences)}\n"
			f"Question: {question}\n"
			f"As {character.name}, answer the question:"
		)
			
			response = openai.Completion.create(
			engine=PREFERRED_ENGINE,
			prompt=prompt,
			max_tokens=100,  # Adjust the number of tokens based on the desired length of the answer
			n=1,
			stop=None,
			temperature=0.7,
		)

		answer = response.choices[0].text.strip()
		return answer
		
class StoryGenerator:
	def __init__(self, characters):
		self.characters = characters

	def generate_story(self):
		# Set up the OpenAI API
		openai.api_key = 'your_openai_api_key_here'

		# Prepare the context for the story generation
		character_descriptions = "\n".join(
			f"{character.name} is a {character.occupation} at the Museum. "
			f"Background: {character.background}. "
			f"Motivations: {', '.join(character.motivations)}. "
			f"Traits: {', '.join(character.traits)}."
			for character in self.characters
		)

		perpetrators = ", ".join(
			character.name for character in self.characters if character.is_perpetrator
		)

		prompt = (
			f"The following characters work at a Museum where there has been a theft of an ancient artifact:\n"
			f"{character_descriptions}\n"
			f"The perpetrator(s) of the theft is/are {perpetrators}."
			f"\nGenerate a story summary including how, when, why, and by whom the theft took place, "
			"what was taken, and what each character was doing during the theft."
		)

		response = openai.Completion.create(
			engine="text-davinci-002",
			prompt=prompt,
			max_tokens=200,  # Adjust the number of tokens based on the desired length of the story summary
			n=1,
			stop=None,
			temperature=0.7,
		)

		story = response.choices[0].text.strip()
		return story

	def compress_story(self, story):
		# Set up the OpenAI API
		openai.api_key = 'your_openai_api_key_here'

		prompt = (
			f"Compress the following story in a way that ChatGPT will be able to later unpack and understand the key details:\n"
			f"{story}\n"
			"Output a compressed version of the story:"
		)

		response = openai.Completion.create(
			engine="text-davinci-002",
			prompt=prompt,
			max_tokens=100,  # Adjust the number of tokens based on the desired length of the compressed story
			n=1,
			stop=None,
			temperature=0.7,
		)

		compressed_story = response.choices[0].text.strip()
		return compressed_story

	def generate_intro_story(self):
		# Set up the OpenAI API
		openai.api_key = 'your_openai_api_key_here'

		character_descriptions = "\n".join(
			f"{character.name} is a {character.occupation}. They are {character.traits}"
			for character in self.characters
		)

		prompt = (
			f"The following characters work at a Museum where there has been a theft of an ancient artifact:\n"
			f"{character_descriptions}\n"
			f"Using the following compressed story as additional context:\n"
			f"{compressed_story}\n"
			f"Generate an introduction story for the player that includes a brief description of the Museum, "
			"the high-level details of the theft, and one or two-word descriptions of the characters. "
			"Do not reveal the perpetrator(s) or specific aspects of the characters' traits."
		)

		response = openai.Completion.create(
			engine="text-davinci-002",
			prompt=prompt,
			max_tokens=150,  # Adjust the number of tokens based on the desired length of the introduction story
			n=1,
			stop=None,
			temperature=0.7,
		)

		intro_story = response.choices[0].text.strip()
		return intro_story

class ExperiencesGenerator:
	def __init__(self, characters, story):
		self.characters = characters
		self.story = story

	def generate_experiences(self):
		# Set up the OpenAI API
		openai.api_key = 'your_openai_api_key_here'

		for character in self.characters:
			prompt = (
				f"The story summary of a museum theft involving the following characters is:\n"
				f"{self.story}\n"
				f"Generate a list of five experiences related to the theft for {character.name}, "
				f"a {character.occupation} at the museum. "
				f"Background: {character.background}. "
				f"Motivations: {', '.join(character.motivations)}. "
				f"Traits: {', '.join(character.traits)}."
			)

			response = openai.Completion.create(
				engine="text-davinci-002",
				prompt=prompt,
				max_tokens=100,  # Adjust the number of tokens based on the desired length of the experiences
				n=1,
				stop=None,
				temperature=0.7,
			)

			experiences = response.choices[0].text.strip().split("\n")
			character.experiences = experiences
