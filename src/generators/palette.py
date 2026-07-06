class WeatherPalette:
    def __init__(self, term, is_day: int, weather_code: int):
        self.term = term
        self.is_day = is_day == 1
        self.is_cloudy = weather_code in [1, 2, 3, 45, 48, 51, 53, 55, 61, 63, 65, 71, 73, 75, 77, 80, 81, 82, 85, 86,
                                          95, 96, 99]
        if self.is_day:
            self.sky_bg = term.on_blue
            self.cloud_color = term.gray if self.is_cloudy else term.white
            self.mountain_far = term.blue
            self.mountain_near = term.green
            self.tree = term.bold_green
            self.hud_title = term.bold_yellow
            self.hud_stats = term.bold_cyan
        else:
            self.sky_bg = term.on_color(17)
            self.cloud_color = term.bright_black
            self.mountain_far = term.bright_black
            self.mountain_near = term.bright_black
            self.tree = term.green
            self.hud_title = term.bold_blue
            self.hud_stats = term.gray
