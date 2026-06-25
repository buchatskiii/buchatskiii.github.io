#!/usr/bin/env python3
"""Ждём DNS и запускаем certbot"""
import paramiko, time, socket

def check_dns(domain):
    try:
        ip = socket.gethostbyname(domain)
        print(f"  {domain} -> {ip}")
        return ip == "139.100.234.22"
    except:
        print(f"  {domain} -> NXDOMAIN")
        return False

print("Ожидаем настройки DNS для beklox.ru...")
print("Убедитесь, что в панели управления доменом добавлены A-записи:")
print("  beklox.ru -> 139.100.234.22")
print("  www.beklox.ru -> 139.100.234.22")
print()

for i in range(60):
    ok1 = check_dns("beklox.ru")
    ok2 = check_dns("www.beklox.ru")
    
    if ok1 and ok2:
        print("\n✅ DNS настроен! Запускаем certbot...")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('139.100.234.22', username='root', password='qmc67Ra9TYas', timeout=30)
        
        stdin,stdout,stderr = client.exec_command(
            'certbot --nginx -d beklox.ru -d www.beklox.ru --non-interactive --agree-tos --email dlyavsego02@mail.ru --redirect 2>&1',
            timeout=120
        )
        result = stdout.read().decode()
        print(result)
        
        # Проверяем результат
        if "Congratulations" in result or "successfully" in result.lower():
            print("\n✅ SSL-сертификат получен!")
            # Перезагружаем nginx
            client.exec_command('systemctl reload nginx', timeout=10)
        else:
            print("\n⚠️ Ошибка при получении сертификата:")
            err = stderr.read().decode()
            if err:
                print(err)
        
        client.close()
        break
    else:
        mins = i // 2
        if i % 2 == 0:
            print(f"⏳ Прошло {mins} мин. DNS ещё не обновлён...")
        time.sleep(30)
else:
    print("\n❌ Таймаут: DNS не обновился за 30 минут.")
    print("Проверьте настройки DNS в панели управления доменом.")
