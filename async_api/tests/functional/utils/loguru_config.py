loguru_config = {
    'sink': './logs/etl.log',
    'format': '{time:MMMM D, YYYY > HH:mm:ss} | {message} | {level}',
    'level': 'INFO',
    'rotation': '00:00',
}
