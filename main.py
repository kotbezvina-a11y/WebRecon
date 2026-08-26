import urllib.request
import urllib.error
import sys

open('wordlist.txt', 'a').close()
open('report.txt', 'a').close()

OPTIONS = [
    'Show menu',
    'Set target',
    'Scan website',
    'Show wordlist',
    'Add path',
    'Remove path',
    'Save report',
    'View result',
    'Analyze result',
    'Exit'
]

target_url = None

scan_result, analysis, raw_data = {}, [], []

def menu():
    print('========================')
    print('      WebRecon')
    print('========================\n')

    if target_url:
        print(f'Selected address: {target_url}\n')

    for index, option in enumerate(OPTIONS, start=1):
        print(f'{index}. {option}')

def set_target():
    global target_url
    print('\n!!!WARNING!!!')
    print(
        'The option accepts only full-format'
        'URLs with case sensitivity!'
    )
    print(
        'Specify the URL in the following format: '
        'https://www.google.com or http://www.google.com!\n'
    )

    set_target_cmd = input('Enter the address: ')

    if set_target_cmd.startswith('https://') or set_target_cmd.startswith('http://'):
        if set_target_cmd.rstrip('/'):
            target_url = set_target_cmd.rstrip('/')
        else:
            target_url = set_target_cmd
    else:
        print('Specify the data transfer protocol!')


def scan_website():
    url_error = False
    REQUEST_TIMEOUT = 5

    if target_url:
        with open('wordlist.txt', 'r') as f:
            scan_result.clear()
            for line in f:
                line = line.rstrip('\n')
                if not line.startswith('/'):
                    line = '/' + line
                if line.endswith('/') and len(line) > 1:
                    line = line.rstrip('/')
                scan_result[line] = {}
                scan_result[line]['Status'] = 'Waiting'
                scan_result[line]['Size'] = None

            for url_key in scan_result.keys():
                request = urllib.request.Request(
                    target_url + url_key,
                    method="HEAD"
                )

                try:
                    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                        scan_result[url_key]['Status'] = response.status
                        raw_size = response.headers.get('Content-Length')

                        if raw_size and raw_size.strip().isdigit():
                            scan_result[url_key]['Size'] = int(raw_size)
                        else:
                            scan_result[url_key]['Size'] = 0

                except urllib.error.HTTPError as e:
                    scan_result[url_key]['Status'] = e.code
                    raw_size = e.headers.get('Content-Length')
                    scan_result[url_key]['Size'] = int(raw_size) if raw_size is not None else 0

                    if not scan_result[url_key]['Size']:
                        scan_result[url_key]['Size'] = 0

                except urllib.error.URLError as e:
                    scan_result[url_key]['Status'] = 'URL-Error'
                    scan_result[url_key]['Size'] = 0

                    if not url_error:
                        print(
                            f'\nERROR! It seems you have specified a non-existent URL'
                              'or you do not have an internet connection!'
                        )
                        debugger_instruction = input('Show error details? (y/n): ')

                        if debugger_instruction == 'y' or debugger_instruction == 'n':
                            url_error = True

                    if debugger_instruction == 'y':
                        print(f'{url_key} {e}\n')
                    elif debugger_instruction == 'n':
                        break
                    else:
                        print('Non-existent option!')

            print('\nScan completed successfully!')
            while True:
                pop_up = input('Would you like to view the scan results? (y/n): ')

                if pop_up == 'y':
                    view_result()
                    break

                elif pop_up == 'n':
                    break

                else:
                    print('Unknown argument!')

    else:
        print('No URL address selected!')

        while True:
            pop_up = input('Would you like to proceed to URL input? (y/n): ')

            if pop_up == 'y':
                set_target()
                scan_website()
                break
            elif pop_up == 'n':
                break
            else:
                print('Invalid argument!')


def show_wordlist():
    with open('wordlist.txt', 'r') as f:
        for index, line in enumerate(f, start=1):
            print(f"[{index}] {line.rstrip('\n')}")

def add_path():
    add_path_cmd = input('Enter the path: ')

    with open('wordlist.txt', 'a') as f:
        f.write(f'\n{add_path_cmd}')

def remove_path():
    with open('wordlist.txt', 'r') as f:
        lines = f.readlines()

    for index, path in enumerate(lines, start=1):
        print(f"[{index}] {path.rstrip('\n')}")

    try:
        remove_path_cmd = int(input('\nEnter the number of the item to delete: ')) - 1

        if 0 <= remove_path_cmd < len(lines):
            lines.pop(remove_path_cmd)

            with open('wordlist.txt', 'w') as f:
                f.writelines(lines)
        else:
            print('Non-existent index!')

    except ValueError:
        print('Unknown index!')

def save_report():
    with open('report.txt', 'w') as report:
        report.write('========== WebRecon Report ==========')
        report.write(f'\nTarget-URL: {target_url}\n')

        with open('wordlist.txt', 'r') as f:
            count_words = len(f.readlines())
            report.write(f'Wordlist entries: {count_words}\n')

        print('The following analysis has been added to the report:\n')
        analyze_result()
        for line in analysis:
            report.write(line + '\n')

        if scan_result:
            while True:
                pop_up = input('\nWould you like to add the raw data to the report?(y/n): ')

                if pop_up == 'y':
                    view_result()
                    for line in raw_data:
                        report.write(line + '\n')
                    break
                elif pop_up == 'n':
                    break
                else:
                    print('Invalid argument!')

        report.write('\n=========== END REPORT ===========')

def view_result():
    raw_data.clear()

    if not scan_result:
        print('Scan results are missing!')

        while True:
            pop_up = input('Would you like to perform an automatic scan? (y/n): ')

            if pop_up == 'y':
                if not target_url:
                    set_target()
                scan_website()
                return
            elif pop_up == 'n':
                break
            else:
                print('Invalid argument!')
    else:
        raw_data.append('========== RESULTS ==========\n')
        for index, (key, value) in enumerate(scan_result.items(), start=1):
            status = value.get('Status')
            size = value.get('Size')
            raw_data.append(
                f'[{index}] {key:<20} | {status} | {size} bytes'
            )
        raw_data.append('\n=============================')

    for line in raw_data:
        print(line)

def analyze_result():
    analysis.clear()

    status_count = {
        200: 0,
        301: 0,
        403: 0,
        404: 0
    }
    INTERESTING_PATHS = [
        '/admin',
        '/backup.zip',
        '/config.php.bak',
        '/robots.txt'
    ]

    analysis.append('========== ANALYSIS ==========\n')

    with open('wordlist.txt', 'r') as f:
        analysis.append(f'Total paths: {len(f.readlines())}\n')

    analysis.append('Scan result:\n')

    if scan_result:
        analysis.append('Status-code detected:')
        for index, (key, value) in enumerate(scan_result.items(), start=1):
            status = value.get('Status')

            if status in status_count:
                status_count[status] += 1
            else:
                continue

        analysis.append(f'200 OK: {status_count[200]}')
        analysis.append(f'301 Redirect: {status_count[301]}')
        analysis.append(f'403 Forbidden: {status_count[403]}')
        analysis.append(f'404 Not Found: {status_count[404]}\n')

        analysis.append('Interesting paths:')
        for key, value in scan_result.items():
            status = value.get('Status')

            if (
                key in INTERESTING_PATHS
                and status in (200, 301, 403)
            ):
                analysis.append(f'{key}: {status}')

        analysis.append('\nLargest response:')

        key_size = None
        max_size = 0

        for key, value in scan_result.items():
            size = value.get('Size')

            if size:
                if size > max_size:
                    key_size = key
                    max_size = size

        analysis.append(f'{key_size}: {max_size}')
    else:
        analysis.append('Scan results not found!')

    analysis.append('\n==============================')

    for line in analysis:
        print(line)


def exit_program():
    print('Terminating process...')
    sys.exit()

menu()

actions = {
    1: menu,
    2: set_target,
    3: scan_website,
    4: show_wordlist,
    5: add_path,
    6: remove_path,
    7: save_report,
    8: view_result,
    9: analyze_result,
    10: exit_program
}

while True:
    try:
        cmd = int(input('\nSelect an option: '))

        if cmd in actions:
            actions[cmd]()
        else:
            print('Non-existent option!')

    except ValueError:
        print('Invalid option!')
