import os

from flask_discord import DiscordOAuth2Session


def initialize_discord_auth(app):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
    app.config["DISCORD_CLIENT_ID"] = os.environ.get('DISCORD_CLIENT_ID')
    app.config["DISCORD_CLIENT_SECRET"] = os.environ.get('DISCORD_CLIENT_SECRET')
    app.config["DISCORD_REDIRECT_URI"] = os.environ.get('DISCORD_REDIRECT_URI')

    app.config['DISCORD_AUTH_SETTINGS'] = {
        'guildId': os.environ.get('DISCORD_AUTH_GUILD_ID'),
        'adminRole': os.environ.get('DISCORD_AUTH_ADMIN_ROLE'),
        'teamManagerRole': os.environ.get('DISCORD_AUTH_TEAM_MANAGER_ROLE'),
    }

    return DiscordOAuth2Session(app)
