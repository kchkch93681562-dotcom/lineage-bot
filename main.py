import os; os.environ["discord_cloudflare_bypass"] = "true"
import discord
from discord.ext import commands
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_MAPPING = {
    1491210246805524520: {
        "channel_name": "⚔️ 지휘 메인보스",
        "text_channel_id": 1516057402569654394,
        "color": 0x3498db
    },
    1491207559896498338: {
        "channel_name": "🔊 나이트-수다방",
        "text_channel_id": 1491206924547395665,
        "color": 0x9b59b6
    }
}

TARGET_TAGS = ["[나이트]", "[인천]"]
status_messages = {}

@bot.event
async def on_ready():
    print(f"봇 로그인 완료: {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    active_channels = []
    if before.channel and before.channel.id in CHANNEL_MAPPING:
        active_channels.append(before.channel.id)
    if after.channel and after.channel.id in CHANNEL_MAPPING:
        if after.channel.id not in active_channels:
            active_channels.append(after.channel.id)

    for voice_id in active_channels:
        config = CHANNEL_MAPPING[voice_id]
        voice_channel = guild.get_channel(voice_id)
        text_channel = guild.get_channel(config["text_channel_id"])

        if not voice_channel or not text_channel:
            continue

        stats = {tag: 0 for tag in TARGET_TAGS}
        unknown_count = 0
        total_users = len(voice_channel.members)

        for m in voice_channel.members:
            name = m.display_name
            matched = False
            for tag in TARGET_TAGS:
                if tag in name:
                    stats[tag] += 1
                    matched = True
                    break
            if not matched:
                unknown_count += 1

        embed = discord.Embed(
            title=f"📊 {config['channel_name']}",
            description=f"**실시간 채널 접속 현황**\n\n🟢 현재 총 **{total_users}명** 접속 중",
            color=config["color"]
        )

        stat_entries = []
        for tag, count in stats.items():
            if count > 0:
                stat_entries.append(f"**{tag}** {count}명")
        if unknown_count > 0:
            stat_entries.append(f"**[기타/미설정]** {unknown_count}명")

        if total_users > 0:
            embed.add_field(name="👥 소속별 인원", value=" ｜ ".join(stat_entries), inline=False)
        else:
            embed.add_field(name="📢 상태", value="📢 현재 채널이 비어있습니다.", inline=False)

        embed.set_footer(text="실시간 자동 갱신 현황판")

        try:
            msg = status_messages.get(voice_id)
            if msg:
                await msg.edit(embed=embed)
            else:
                await text_channel.purge(limit=3)
                new_msg = await text_channel.send(embed=embed)
                status_messages[voice_id] = new_msg
        except Exception as e:
            print(f"{config['channel_name']} 업데이트 실패: {e}")
            status_messages[voice_id] = None

# Render 무료 웹서버 가짜 포트 개방용 코드 (에러 방지 필수)
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"가짜 웹서버 구동 중 (포트: {port})")
    server.serve_forever()

# 백그라운드에서 가짜 웹서버를 돌려 Render의 수면 차단 및 에러를 예방합니다.
threading.Thread(target=run_dummy_server, daemon=True).start()

bot.run(os.environ.get('DISCORD_TOKEN'))

