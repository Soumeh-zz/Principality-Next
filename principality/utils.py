from nextcord import ChannelType, Embed, MessageType, Message
from json import loads
from urllib.request import urlopen

def message_as_embed(message: Message) -> Embed:
    embed_message = message.content
    #if message.content == None:
    #    raise EmptyMessage("Message is embeded or is a system \\\\\message")
    #if message.embeds != []:
    #    return await message.channel.send("Cannot send Embeded messages (yet).")
    if message.type == MessageType.pins_add:
        embed_message = f"{message.author.display_name} pinned a message to this channel. See all the pins."
    elif message.type == MessageType.new_member:
        embed_message = f"{message.author.display_name} Joined the server."
    embed = Embed(description=embed_message + f'\n\n[(jump)]({message.jump_url})', timestamp=message.created_at)
    embed.set_author(url='https://discord.com/users/{}'.format(message.author.id), name=message.author.name, icon_url=message.author.display_avatar.url)
    if message.channel.type == ChannelType.text: embed.set_footer(text=f'#{message.channel.name}')
    this_attachment = (message.attachments[0:]+[None])[0]
    if this_attachment != None:
        if this_attachment.filename.endswith(('.png', '.gif', '.jpeg', '.jpg', '.webp')):
            embed.set_image(url=this_attachment.url)
        else:
            embed.description = message.content + f'\n[<{this_attachment.filename}>]({this_attachment.url})\n\n[(jump)]({message.jump_url})'
    
    if message.embeds:
        embeds = [embed]
        embeds.extend(message.embeds)
        return embeds
    return embed

def url_to_json(url):
    with urlopen(url) as url:
        return loads(url.read().decode())