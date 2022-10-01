import time as t
from datetime import  timedelta
from tzlocal import get_localzone
from PIL import Image, ImageFont, ImageDraw, ImageSequence
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

    def __render_game(self):
        while True:
            debug.info("Starting render.")
            # If we need to refresh the overview data, do that
            if self.data.needs_refresh:
                self.data.refresh_games()

            basic_game = self.data.games[self.data.current_game_index]
            

            # Set the refresh rate
            rotate_rate = self.__rotate_rate_for_game(basic_game)
            refresh_rate = self.data.config.data_refresh_rate
            debug.info(f'Refresh rate: {refresh_rate}s')

            # Draw the current game
            self.__draw_game(basic_game)
            t.sleep(rotate_rate)
            
            endtime = t.time()
            time_delta = endtime - self.starttime

            if time_delta >= refresh_rate and self.data.needs_refresh:
                self.starttime = t.time()
                self.data.needs_refresh = True
                debug.info("Needs refresh!")

            if endtime - self.data.games_refresh_time >= refresh_rate:
                self.data.needs_refresh = True
                debug.info("Needs refresh!")
            
            if self.__should_rotate_to_next_game(basic_game):
                if self.data.needs_refresh:
                    self.data.refresh_games()
                return self.data.advance_to_next_game()

    def __rotate_rate_for_game(self, game):
        if game['state'] == 'Pre-Game':
            rotate_rate = self.data.config.rotation_rates_pregame
            debug.info(f'Setting pre-game rotation rate: {rotate_rate}s')
        elif game['state'] == 'Final':
            rotate_rate = self.data.config.rotation_rates_final
            debug.info(f'Setting post game rotation rate: {rotate_rate}s')
        else:
            rotate_rate = self.data.config.rotation_rates_live
            debug.info(f'Setting rotation rate: {rotate_rate}s')
        return rotate_rate

    def __should_rotate_to_next_game(self, game):
        rotate = False
        should_rotate = self.data.config.rotation_enabled
        live_game = self.data.showing_preferred_game()
        live_rotate = live_game and self.data.config.rotation_preferred_team_live_enabled
        halftime_rotate = live_game and self.data.config.rotation_preferred_team_live_halftime

        if halftime_rotate and hasattr(game, 'play_by_play') and game['play_by_play'][-1]['play_result_type_id'] == 8:
            debug.info("Halftime rotate!")
            rotate = True
        elif live_rotate and live_game:
            debug.info("Live rotate!")
            rotate = True

        debug.info(f'__should_rotate_to_next_game? {rotate}')
        return rotate and should_rotate

    def __draw_game(self, game):
        debug.info(f'Drawing game. __draw_game({game["id"]})')
        
        gametime = self.data.get_gametime()
        one_hour_pregame = gametime - timedelta(hours=1)

        if game['state'] == 'Final':
            debug.info('State: Post-Game')
            self._draw_post_game(game)
            #game = self.data.current_game()
            #self._draw_live_game(game)
        elif gametime.now(get_localzone()) > one_hour_pregame and game['state'] == 'Pre-Game':
            debug.info('Countdown til gametime')
            self._draw_countdown(game)
        elif game['state'] == 'Pre-Game':
            debug.info('State: Pre-Game')
            self._draw_pregame(game)
        elif game['state'] == 'Postponed' or game['state'] == 'Cancelled':
            self.data.advance_to_next_game()
            self.__render_game()
        else:
            game = self.data.current_game()
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
        game_time = self.data.get_gametime()
        if not time < game_time:
            gametime = f'Kickoff!'
        else:
            gt_diff = game_time - time
            min_to_go = round(gt_diff.total_seconds() / 60)
            gametime = f'{min_to_go} min'
            
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

    def _draw_live_game(self, game):
        homescore = '{0:02d}'.format(game['home_score'])
        awayscore = '{0:02d}'.format(game['away_score'])
        last_play_code = game['play_result_type_id']

        # Use this code if you want the animations to run
        if last_play_code == 1:
            debug.info('should draw TD')
            self._draw_td()
        elif last_play_code == 2:
            debug.info('should draw FG')
            self._draw_fg()
        # Prepare the data
        # score = '{}-{}'.format(overview['away_score'], overview['home_score'])
        quarter = f"Q{game['quarter']}"
        
        minutes = f"{game['minutes']}" if game['minutes'] else None
        seconds = f"{game['seconds']}" if game['seconds'] else None
        time_period = f"{minutes}:{seconds}" if minutes and seconds else ""
        pos_colour = (255, 255, 255)
        if game['redzone']:
            pos_colour = (255, 25, 25)
        if game['possession']:
            pos = game['possession']
            info_pos = center_text(self.font_mini.getsize(str(pos))[0], 32)
            self.draw.multiline_text((info_pos, 13), str(pos), fill=(pos_colour), font=self.font_mini, align="center")
        if game['down'] and game['ytg']:
            down = f"{game['down']}&{game['ytg']}"
            info_pos = center_text(self.font_mini.getsize(str(down))[0], 32)
            self.draw.multiline_text((info_pos, 19), str(down), fill=(pos_colour), font=self.font_mini, align="center")
        if game['spot']:
            spot = f"{game['spot']}"
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
        
        self.data.needs_refresh = True
        
        # Check if the game is over
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
        
        self.data.needs_refresh = False

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
