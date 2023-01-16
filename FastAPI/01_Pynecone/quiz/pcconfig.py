import pynecone as pc


config = pc.Config(
    app_name="quiz",
    api_url="0.0.0.0:30003",
    bun_path="$HOME/.bun/bin/bun",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
