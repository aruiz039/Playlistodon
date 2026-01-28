from mastodon import Mastodon

mastodon = Mastodon(
    access_token= "token.secret",
    api_base_url= "https://social.completext.com/"
)


timeline = mastodon.timeline_hashtag("TuesdayTracks")
for status in timeline:
    card = status.get("card")
    if card and "url" in card:
        url = card["url"]
        if "youtube.com" in url or "youtu.be" in url:
            print(url)

