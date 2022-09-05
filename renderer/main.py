import time as t
from datetime import datetime, timedelta
from dateutil import parser
from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from data.cfl_api import cfl_api_parser
from utils import center_text
from renderer.screen_config import screenConfig
import debug

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)

    def render(self):
        while True:
            self.starttime = t.time()
            self.data.get_current_date()
            self.__render_game()
#            self._draw_post_game()

    def __render_game(self):
        while True:
            debug.info("Starting render.")
            # If we need to refresh the overview data, do that
            if self.data.needs_refresh:
                self.data.refresh_games()
                
            basic_game = self.data.games[self.data.current_game_index]

            # Draw the current game
            self.__draw_game(basic_game)

            # Set the refresh rate
            rotate_rate = self.__rotate_rate_for_game(basic_game)
            t.sleep(rotate_rate)
            endtime = t.time()
            time_delta = endtime - self.starttime

            # If we're ready to rotate, let's do it
            # fix this u idiot
            if time_delta >= rotate_rate and self.data.needs_refresh:
                self.starttime = t.time()
                self.data.needs_refresh = True
                debug.info("Needs refresh!")

            if self.__should_rotate_to_next_game(self.data.games[self.data.current_game_index]):
                return self.data.advance_to_next_game()

            if endtime - self.data.games_refresh_time >= rotate_rate:
                self.data.refresh_games()


    def __rotate_rate_for_game(self, game):
        if game['state'] == 'Pre-Game':
            rotate_rate = self.data.config.rotation_rates_pregame
            debug.info(f'Setting pre-game rotation rate: {rotate_rate}')
        elif game['state'] == 'Final':
            rotate_rate = self.data.config.rotation_rates_final
            debug.info(f'Setting post game rotation rate: {rotate_rate}')
        else:
            rotate_rate = self.data.config.rotation_rates_live
            debug.info(f'Setting rotation rate: {rotate_rate}')
        return rotate_rate

    def __should_rotate_to_next_game(self, game):
        debug.info(f"__should_rotate_to_next_game({game})")
        #game_details = cfl_api_parser.get_overview(game['id'])
        #halftime_rotate = game_details['play_by_play'][-1]['play_result_type_id'] == 8 and self.data.config.rotation_preferred_team_live_halftime
        return self.data.config.rotation_enabled and self.data.config.rotation_preferred_team_live_enabled

    def __draw_game(self, game):
        debug.info('Drawing game. __draw_game()')

        if game['state'] == 'Final':
            debug.info('State: Post-Game')
            self._draw_post_game(game)
        else:
            game = self.data.current_game()
            time = self.data.get_current_date()
            gamedatetime = self.data.get_gametime()
            
            if time < gamedatetime - timedelta(hours=1) and game['state'] == 'Pre-Game':
                debug.info('State: Pre-Game')
                self._draw_pregame(game)
            elif time < gamedatetime and game['state'] == 'Pre-Game':
                debug.info('Countdown til gametime')
                self._draw_countdown(game)
            else:
                debug.info(f'State: Live Game, checking every {self.__rotate_rate_for_game(game)}s')
                self._draw_live_game(game)

    def _draw_pregame(self, game):
            time = self.data.get_current_date()
            gamedatetime = self.data.get_gametime()
            if gamedatetime.day == time.day and gamedatetime.month == time.month:
                date_text = 'TODAY'
            else:
                date_text = gamedatetime.strftime('%A %-d %b').upper()
            gametime = gamedatetime.strftime("%-I:%M %p")
            # Center the game time on screen.                
            date_pos = center_text(self.font_mini.getsize(date_text)[0], 32)
            gametime_pos = center_text(self.font_mini.getsize(gametime)[0], 32)
            # Draw the text on the Data image.
            self.draw.text((date_pos, 0), date_text, font=self.font_mini)
            self.draw.multiline_text((gametime_pos, 6), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 15), 'VS', font=self.font)
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # TEMP Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(game['away_team_abbrev'].lower())).resize((20, 20), Image.BOX)
            home_team_logo = Image.open('logos/{}.png'.format(game['home_team_abbrev'].lower())).resize((20, 20), Image.BOX)
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), 1, 12)
            self.canvas.SetImage(home_team_logo.convert("RGB"), 43, 12)
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_countdown(self, game):
        time = self.data.get_current_date()
        gametime = self.data.get_gametime()
        if time < gametime:
            gt = gametime - time
            # as beautiful as I am
            if gt > timedelta(hours=1):
                gametime = ':'.join(str(gametime - time).split(':')[:2])
            else:
                gametime = ':'.join(str(gametime - time).split(':')[1:]).split('.')[:1][0]
            # Center the game time on screen.
            gametime_pos = center_text(self.font_mini.getsize(gametime)[0], 32)
            # Draw the text on the Data image.
            self.draw.text((29, 0), 'IN', font=self.font_mini)
            self.draw.multiline_text((gametime_pos, 6), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 15), 'VS', font=self.font)
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # TEMP Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(game['away_team_abbrev'].lower())).resize((20, 20), Image.BOX)
            home_team_logo = Image.open('logos/{}.png'.format(game['home_team_abbrev'].lower())).resize((20, 20), Image.BOX)
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), 1, 12)
            self.canvas.SetImage(home_team_logo.convert("RGB"), 43, 12)

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
            # t.sleep(1)
        else:
            self._draw_game(game)

    def _draw_live_game(self, game):
        homescore = '{0:02d}'.format(game['home_score'])
        awayscore = '{0:02d}'.format(game['away_score'])

        # Refresh the data
        #if self.data.needs_refresh:
            #debug.info('Refresh game overview')
            #self.data.refresh_games()
            #self.data.needs_refresh = False
        # Use this code if you want the animations to run
        if game['home_score'] > int(homescore) + 5 or game['away_score'] > int(awayscore) + 5:
            debug.info('should draw TD')
            self._draw_td()
        elif game['home_score'] > int(homescore) + 2 or game['away_score'] > int(awayscore) + 2:
            debug.info('should draw FG')
            self._draw_fg()
        # Prepare the data
        # score = '{}-{}'.format(overview['away_score'], overview['home_score'])
        quarter = f"Q{game['quarter']}"
        time_period = game['time']
        pos = None
        down = None
        spot = None
        # FIX ME FOR CFL DATA SPEC - get from play_by_play from individual games data
        #if game['possession'] == game['away_team_id']:
        #    pos = game['away_team_abbrev']
        #else:
        #    pos = game['home_team_abbrev']
        pos_colour = (255, 255, 255)
        if game['redzone']:
            pos_colour = (255, 25, 25)
        if game['down']:
            down = f"DN: {game['down']}"
            info_pos = center_text(self.font_mini.getsize(str(down))[0], 32)
            self.draw.multiline_text((info_pos, 19), str(down), fill=(pos_colour), font=self.font_mini, align="center")
        if game['spot']:
            spot = f"YTG: {game['spot']}"
            info_pos = center_text(self.font_mini.getsize(spot)[0], 32)
            self.draw.multiline_text((info_pos, 25), spot, fill=(pos_colour), font=self.font_mini, align="center")
        # Set the position of the information on screen.
        home_score_size = self.font.getsize(homescore)[0]
        time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 32)
        quarter_pos = center_text(self.font_mini.getsize(quarter)[0], 32)

        self.draw.multiline_text((quarter_pos, 0), quarter, fill=(255, 255, 255), font=self.font_mini, align="center")
        self.draw.multiline_text((time_period_pos, 6), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")
        self.draw.multiline_text((6, 19), awayscore, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((59 - home_score_size, 19), homescore, fill=(255, 255, 255), font=self.font, align="center")
        
        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)
        
        # TEMP Open the logo image file
        away_team_logo = Image.open('logos/{}.png'.format(game['away_team_abbrev'].lower())).resize((20, 20), Image.BOX)
        home_team_logo = Image.open('logos/{}.png'.format(game['home_team_abbrev'].lower())).resize((20, 20), Image.BOX)
        
        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), 1, 0)
        self.canvas.SetImage(home_team_logo.convert("RGB"), 43, 0)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Check if the game is over
        self.data.needs_refresh = True
        
        if game['state'] == 'Final':
            debug.info('GAME OVER')
            self.data.needs_refresh = False

    def _draw_post_game(self, game):
        # Prepare the data
        score = '{}-{}'.format(game['away_score'], game['home_score'])
        # Set the position of the information on screen.
        score_position = center_text(self.font.getsize(score)[0], 32)
        # Draw the text on the Data image.
        self.draw.multiline_text((score_position, 19), score, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((24, 0), "FINAL", fill=(255, 255, 255), font=self.font_mini,align="center")
        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)
        # TEMP Open the logo image file
        away_team_logo = Image.open('logos/{}.png'.format(game['away_team_abbrev'].lower())).resize((20, 20), Image.BOX)
        home_team_logo = Image.open('logos/{}.png'.format(game['home_team_abbrev'].lower())).resize((20, 20), Image.BOX)
        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), 1, 0)
        self.canvas.SetImage(home_team_logo.convert("RGB"), 43, 0)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_td(self):
        debug.info('TD')
        # Load the gif file
        ball = Image.open("assets/td_ball.gif")
        words = Image.open("assets/td_words.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        x = 0
        while x is not 3:
            try:
                ball.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                ball.seek(frameNo)
            self.canvas.SetImage(ball.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.05)
        x = 0
        while x is not 3:
            try:
                words.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                words.seek(frameNo)
            self.canvas.SetImage(words.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.05)

    def _draw_fg(self):
        debug.info('FG')
        # Load the gif file
        im = Image.open("assets/fg.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        x = 0
        while x is not 3:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)
            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.02)
