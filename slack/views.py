from flask import Flask, request
from slack.models import Memegen, Slack, parse_text_into_params, image_exists

app = Flask(__name__)
memegen = Memegen()
slack = Slack()

@app.route("/", methods=["GET", "POST"])
def meme():
    data = request.form if request.method == 'POST' else request.args
    token, text, channel_id, user_id = [data[key] for key in ("token", "text", "channel_id", "user_id")]
    text = text.strip()

    if token != slack.SLASH_COMMAND_TOKEN:
        return "Unauthorized."

    if text.lower() in ("help", ""):
        return memegen.help()

    if text.lower() == "templates":
        return memegen.template_list
    print("Starting...")
    template, top, bottom = parse_text_into_params(text)
    print("Parsed Command... Template : " + template)
    print("Valid Templates :" + str(memegen.valid_templates))
    if template in memegen.valid_templates:
        print("Valid template...")
        meme_url = memegen.build_url(template, top, bottom)
        print("Built URL : " + str(meme_url))
    elif image_exists(template):
        print("Image exists !")
        meme_url = memegen.build_url("custom", top, bottom, template)
        print("Built URL : " + str(meme_url))
    else:
        print("No template !")
        return memegen.bad_template(template)

    payload = {"channel": channel_id}
    print(payload)
    user = slack.find_user_info(user_id)
    print(user)
    payload.update(user)
    
    attachments = [{"image_url": meme_url, "fallback": "; ".join([top, bottom])}]
    payload.update({"attachments": attachments})
    print(payload)
    try:
        slack.post_meme_to_webhook(payload)
    except Exception as e:
        print("Error while responding")
        return e

    return "Success!", 200
