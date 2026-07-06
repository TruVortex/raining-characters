import datetime
import sys

from blessed import Terminal

from src.generators.landscape import LandscapeGenerator
from src.generators.palette import WeatherPalette
from src.terminal_ui import ScreenBuffer
from src.weather_api import WeatherAPI


def main():
    api = WeatherAPI()
    city_input = input("Enter a city name: ").strip()
    if not city_input:
        print("No city entered. Exiting.")
        return
    print(f"Resolving coordinates for '{city_input}'...")
    geo_data = api.get_coordinates(city_input)
    if not geo_data:
        print(f"Could not find coordinates for city: '{city_input}'. Exiting.")
        return
    lat, lon, country, resolved_name, elevation = geo_data
    print(f"Found: {resolved_name}, {country} ({lat:.2f}, {lon:.2f})")
    print(f"Elevation: {elevation:.1f} m asl")
    print("Fetching live weather data...")
    weather_data = api.get_weather(lat, lon)
    if not weather_data:
        print("Failed to retrieve weather data. Exiting.")
        return
    term = Terminal()
    view_width = 80
    view_height = 24
    buffer = ScreenBuffer(view_width, view_height)
    landscape = LandscapeGenerator(view_width, view_height)
    scroll_offset = 0
    frame_count = 0
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)
        while True:
            palette = WeatherPalette(term, weather_data["is_day"], weather_data["weather_code"])
            buffer.clear(palette.sky_bg)
            landscape.generate_terrain(
                buffer,
                palette,
                weather_data["weather_code"],
                elevation,
                scroll_offset
            )
            for x in range(view_width):
                buffer.set_cell(x, 0, "#", term.gray)
                buffer.set_cell(x, view_height - 1, "#", term.gray)
            for y in range(view_height):
                buffer.set_cell(0, y, "#", term.gray)
                buffer.set_cell(view_width - 1, y, "#", term.gray)
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            local_time = utc_now + datetime.timedelta(seconds=weather_data["utc_offset"])
            local_time_str = local_time.strftime("%I:%M %p")
            if local_time_str.startswith("0"):
                local_time_str = local_time_str[1:]
            desc = api.translate_wmo_code(weather_data["weather_code"])
            title = f" {resolved_name}, {country} | {local_time_str} "
            stats = f" {desc} | Temp: {weather_data['temp']}°C (Feels {weather_data['apparent_temp']}°C) | Wind: {weather_data['wind_speed']} km/h "
            controls = " [Esc / 'q' to Quit] "
            start_title_x = max(2, (view_width - len(title)) // 2)
            start_stats_x = max(2, (view_width - len(stats)) // 2)
            start_controls_x = max(2, (view_width - len(controls)) // 2)
            for i, char in enumerate(title):
                buffer.set_cell(start_title_x + i, 2, char, lambda char: palette.sky_bg(palette.hud_title(char)))
            for i, char in enumerate(stats):
                buffer.set_cell(start_stats_x + i, 3, char, lambda char: palette.sky_bg(palette.hud_stats(char)))
            for i, char in enumerate(controls):
                buffer.set_cell(start_controls_x + i, view_height - 2, char, lambda char: palette.sky_bg(term.gray(char)))
            sys.stdout.write(term.home + buffer.draw())
            sys.stdout.flush()
            if frame_count % 5 == 0:
                scroll_offset += 1
            frame_count += 1
            key = term.inkey(timeout=0.08)
            if key == 'q' or key.code == term.KEY_ESCAPE:
                break


if __name__ == "__main__":
    main()
