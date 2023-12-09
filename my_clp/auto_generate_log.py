import random
import re
import string
import threading
import typing
from tqdm import tqdm
from datetime import datetime, timedelta

log_templates = [
    # "{datatime} INFO System startup completed.",
    "{datetime} INFO System startup completed.",
    "{datetime} WARNING User '{username}' login attempt failed from IP {ip_address}.",
    "{datetime} ERROR Database '{database_name}' connection timeout.",
    "{datetime} DEBUG Network configuration changed by user '{username}'.",
    "{datetime} INFO File '{file_path}' accessed by user '{username}'.",
    "{datetime} CRITICAL Disk usage exceeded {percentage} on server '{server_name}'.",
    "{datetime} INFO User '{username}' logged out.",
    "{datetime} ERROR Failed to send email to '{email_address}'.",
    "{datetime} INFO Backup started for directory '{file_path}'.",
    "{datetime} WARNING CPU temperature high on machine '{machine_name}': {temperature}°C.",
    "{datetime} INFO VPN connection established with IP {ip_address}.",
    "{datetime} INFO Scheduled task '{task_name}' executed.",
    "{datetime} ALERT Unauthorized access attempt on port {port} from IP {ip_address}.",
    "{datetime} INFO Service '{service_name}' restarted successfully.",
    "{datetime} INFO Package '{package_name}' updated to version {version}.",
    "{datetime} INFO New user account created: Username '{username}'.",
    "{datetime} WARNING Memory usage high on application '{application_name}': {percentage}%.",
    "{datetime} ERROR License key validation failed for software '{software_name}'.",
    "{datetime} INFO Data export completed: {record_count} records exported.",
    "{datetime} INFO User '{username}' changed their password.",
    "{datetime} CRITICAL Power outage detected in data center '{data_center_name}'.",
    "{datetime} DEBUG API request '{api_path}' received from IP {ip_address}.",
    "{datetime} INFO User '{username}' granted '{role}' role.",
    "{datetime} WARNING Low disk space on '{disk_path}': {remaining_percentage}% remaining.",
    "{datetime} ERROR Malware detected in file '{file_path}'.",
    "{datetime} INFO New network device detected: MAC address {mac_address}.",
    "{datetime} CRITICAL System kernel panic on host '{host_name}'.",
    "{datetime} INFO Document '{file_name}' printed by user '{username}'.",
    "{datetime} WARNING High response time for service '{service_name}': {response_time} ms.",
    "{datetime} ERROR SMTP server '{server_address}' unreachable.",
    "{datetime} INFO SSH key added for user '{username}'.",
    "{datetime} DEBUG '{module_name}' module loaded successfully.",
    "{datetime} ALERT Firewall rule updated: Rule ID {rule_id} allowed for IP {ip_address}.",
    "{datetime} INFO Mobile device '{device_name}' connected to Wi-Fi network '{network_name}'.",
    "{datetime} CRITICAL Application '{application_name}' response time exceeded threshold: {response_time_threshold} ms.",
    "{datetime} INFO User '{username}' accessed the resource '{resource_id}' from IP {ip_address}.",
    "{datetime} WARNING Disk I/O speed slower than expected on device '{device}'.",
    "{datetime} ERROR Connection lost with remote server '{server}'.",
    "{datetime} INFO New session started for user '{username}' at terminal '{terminal}'.",
    "{datetime} ERROR Out of memory error on server '{server}'.",
    "{datetime} DEBUG '{service}' service initiated data refresh cycle.",
    "{datetime} ALERT Intrusion detection system triggered by IP {ip_address}.",
    "{datetime} INFO File '{file_name}' uploaded to bucket '{bucket_name}'.",
    "{datetime} WARNING TLS certificate for domain '{domain}' will expire in {days} days.",
    "{datetime} ERROR Missing dependency '{dependency}' for application '{application}'.",
    "{datetime} INFO Scheduled backup for database '{database_name}' started."

]


def generate_time() -> str:
    # 定义日期的范围
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2023, 12, 31)
    # 生成随机日期
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # 生成随机时间
    random_time = datetime(
        year=random_date.year,
        month=random_date.month,
        day=random_date.day,
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=random.randint(0, 999999)
    )

    # print(random_time)
    return str(random_time)


def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def random_response_time():
    return f"{random.uniform(0.1, 10):.2f}ms"


def random_file_path():
    return '/' + '/'.join(random_string(random.randint(1, 5)) for _ in range(random.randint(1, 5)))


def random_mac():
    return ':'.join(''.join(random.choices('0123456789ABCDEF', k=2)) for _ in range(6))


def random_percentage():
    return f"{random.randint(0, 100)}%"


def random_version():
    return f"{random.randint(0, 10)}.{random.randint(0, 10)}.{random.randint(0, 10)}"


def random_email():
    domains = ["example.com", "mail.com", "test.org"]
    return random_string(7) + "@" + random.choice(domains)


def generate_randon_data() -> dict:
    identifiers_dict = {}
    pattern = r'\{([^}]+)\}'
    for template in log_templates:
        matches = re.findall(pattern, template)
        for identifier in matches:
            if identifier not in identifiers_dict:
                identifiers_dict[identifier] = None

    identifiers_dict["datetime"] = generate_time()
    identifiers_dict["username"] = random_string(random.randint(4, 15))
    identifiers_dict["ip_address"] = random_ip()
    identifiers_dict["database_name"] = f"db_{random.randint(1, 200)}"
    identifiers_dict["file_path"] = random_file_path()
    identifiers_dict["percentage"] = random_percentage()
    identifiers_dict["server_name"] = f"server_{random.randint(1, 200)}"
    identifiers_dict["email_address"] = random_email()
    identifiers_dict["machine_name"] = f"machine_{random.randint(1, 200)}"
    identifiers_dict["temperature"] = random.randint(1, 100)
    identifiers_dict["task_name"] = f"task_{random.randint(1, 200)}"
    identifiers_dict["port"] = random.randint(1024, 65535)
    identifiers_dict["service_name"] = f"service_{random.randint(1, 20)}"
    identifiers_dict["package_name"] = f"package_{random.randint(1, 20)}"
    identifiers_dict["version"] = random_version()
    identifiers_dict["application_name"] = f"app_{random_string()}"
    identifiers_dict["software_name"] = f"software_{random_string()}"
    identifiers_dict["record_count"] = random.randint(1, 10000)
    identifiers_dict["data_center_name"] = f"datacenter_{random.randint(1, 20)}"
    identifiers_dict["api_path"] = f"/api/{random_string()}"
    identifiers_dict["role"] = random.choice(["admin", "user", "guest"])
    identifiers_dict["disk_path"] = random_file_path()
    identifiers_dict["remaining_percentage"] = random_percentage()
    identifiers_dict["mac_address"] = random_mac()
    identifiers_dict["host_name"] = f"host_{random_string()}"
    identifiers_dict["file_name"] = f"{random_string()}.{random.choice(['txt', 'c', 'cpp', 'py', 'js'])}"
    identifiers_dict["response_time"] = random_response_time()
    identifiers_dict["server_address"] = random_ip()
    identifiers_dict["module_name"] = f"module_{random.randint(1, 200)}"
    identifiers_dict["rule_id"] = random.randint(1, 200)
    identifiers_dict["device_name"] = f"device_{random.randint(1, 200)}"
    identifiers_dict["network_name"] = f"net_{random.randint(1, 200)}"
    identifiers_dict["response_time_threshold"] = random_response_time()
    identifiers_dict["resource_id"] = f"resource_{random.randint(1, 200)}"
    identifiers_dict["device"] = f"device_{random.randint(1, 200)}"
    identifiers_dict["server"] = f"server_{random.randint(1, 200)}"
    identifiers_dict["terminal"] = random.randint(1, 200)
    identifiers_dict["service"] = f"server_{random.randint(1, 200)}"
    identifiers_dict["bucket_name"] = f"bucket_{random.randint(1, 200)}"
    identifiers_dict["domain"] = random_string(random.randint(10, 20)) + ".com",
    identifiers_dict["days"] = random.randint(1, 365)
    identifiers_dict["dependency"] = f"dependency_{random.randint(1, 200)}"
    identifiers_dict["application"] = f"app_{random_string()}"

    return identifiers_dict


def main() -> None:
    with open("log_tmp.log", 'w') as file:
        for x in tqdm(range(30000000), desc="generate:"):
            data = generate_randon_data()
            message = random.choice(log_templates).format(**data)
            file.write(message + '\n')
        file.close()


if __name__ == '__main__':
    main()
