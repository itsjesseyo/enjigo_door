import pygame, random


class Speaker:

	def __init__(self, settings):
		#so we can have many different doors
		pygame.mixer.init()
		self.sound_directory = settings.file.get("speaker", "sound_directory")
		self.music = pygame.mixer.music

		self.startup_sound = 'castlevania.mp3'
		self.found_tag_sound = 'mario_coin.mp3'

		self.positve_list = [
			'castlevania.mp3',
			'ark_before_it.mp3',
			'dead_or_alive.mp3',
			'engine.mp3',
			'far_from_self.mp3',
			'not_left_handed.mp3',
			'nothing_you_can.mp3',
			'our_time.mp3',
			'robocop_trouble.mp3',
			'a_shrubbery.mp3',
			'mario_powerup.mp3',
		]

		self.negative_list = [
			'been_bad.mp3',
			'four_weeks.mp3',
			'truffle_shuffle.mp3',
			'go_away_or_taunt.mp3',
			'none_shall_pass.mp3',
			'what_is_fav_color.mp3',
		]

	def play_startup_sound(self):
		print 'playing startup sound'
		pygame.mixer.music.load(self.sound_directory + self.startup_sound)
		pygame.mixer.music.play()

	def play_found_tag_sound(self):
		print 'playing found tag sound'
		pygame.mixer.music.load(self.sound_directory + self.found_tag_sound)
		pygame.mixer.music.play()

	def play_positive_sound(self):
		print 'playing positive sound'
		index = random.randint(0,len(self.positve_list))-1
		pygame.mixer.music.load(self.sound_directory+self.positve_list[index])
		pygame.mixer.music.play()

	def play_negative_sound(self):
		print 'playing negative sound'
		index = random.randint(0,len(self.negative_list))-1
		pygame.mixer.music.load(self.sound_directory+self.negative_list[index])
		pygame.mixer.music.play()




