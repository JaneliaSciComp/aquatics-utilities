import argparse
import os
import sys
import colorlog
import requests

# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
CONN = dict()
CURSOR = dict()

def call_responder(server, endpoint):
    url = CONFIG[server]['url'] + endpoint
    try:
        req = requests.get(url)
    except requests.exceptions.RequestException as err:
        LOGGER.critical(err)
        sys.exit(-1)
    if req.status_code in [200, 404]:
        return req.json()
    LOGGER.error('Status: %s', str(req.status_code))
    sys.exit(-1)


def process_users():
    print("Creating users.txt")
    input = open("User.tsv", "r")
    output = open("users_transient.txt", "w")
    output2 = open("users.txt", "w")
    output.write("ID\tUsername\tFirst name\tLast name\tEmail\n")
    for line in input:
        if line.split("\t")[0] == 'UserID':
            continue
        line = line.strip()
        id = line.split("\t")[0]
        last = line.split("\t")[1]
        email = line.split("\t")[2]
        first = line.split("\t")[6]
        if email:
            uid = email.split('@')[0]
            resp = call_responder('config', 'config/workday/' + uid)
            if 'config' in resp:
                output.write("%s\t%s\t%s\t%s\t%s\n" % (id, uid, resp['config']['first'], resp['config']['last'], resp['config']['email']))
                output2.write("%s\t%s\t%s\t%s\n" % (uid, resp['config']['first'], resp['config']['last'], resp['config']['email']))
                LOGGER.info(uid)
                continue
        if first and last:
            if first == '(null)':
                continue
            uid = last.lower() + first[0].lower()
            uid = uid.replace('-', '')
            resp = call_responder('config', 'config/workday/' + uid)
            if 'config' in resp:
                output.write("%s\t%s\t%s\t%s\t%s\n" % (id, uid, resp['config']['first'], resp['config']['last'], resp['config']['email']))
                output2.write("%s\t%s\t%s\t%s\n" % (uid, resp['config']['first'], resp['config']['last'], resp['config']['email']))
                LOGGER.info(uid)
                continue
            else:
                LOGGER.error("Could not find data for %s", uid)
                output.write("%s\t%s\t%s\t%s\t%s\n" % (id, uid, first, last, 'CORRECT THIS ROW MANUALLY'))
        else:
            LOGGER.error("Incomplete information for %s", line)
    input.close()
    output.close()
    output2.close()


def create_user_dict():
    input = open("users_transient.txt", "r")
    userdict = dict()
    for line in input:
        if line.split("\t")[0] == 'Username':
            continue
        line = line.strip()
        if 'CORRECT' not in line.split("\t")[-1]:
            userdict[line.split("\t")[0]] = line.split("\t")[1]
    input.close()
    os.remove("users_transient.txt") 
    return(userdict)


def process_stocks():
    print("Creating strains.txt")
    input = open("Stock.tsv", "r")
    output = open("strains.txt", "w")
    output.write("StockID\tName\tDate of birth\tUsername\tSpecies\n")
    for line in input:
        if line.split("\t")[0] == 'StockID':
            continue
        line = line.strip()
        field = line.split("\t")
        strain = field[1]
        if field[-2] == '0':
            # LOGGER.warning("Stock %s is not active", strain)
            continue
        if strain == '(null)':
            # LOGGER.warning("Stock ID %s name is null", field[0])
            continue
        userid = field[-1]
        if userid in userdict:
            output.write("%s\t%s\t%s\t%s\t%s\n" % (field[0], strain, field[2].split(' ')[0], userdict[userid], 'zebrafish'))
            LOGGER.info(strain)
        else:
            LOGGER.critical("Could not find user %s", userid)
            sys.exit(-1)
    input.close()
    output.close()


def process_tanks():
    print("Creating tanks.txt")
    input = open("Unit.tsv", "r")
    output = open("tanks.txt", "w")
    output.write("StockID\tName\tUsername\tAmount\t# males\t# females\tBirthdate\n")
    for line in input:
        if line.split("\t")[0] == 'Name':
            continue
        line = line.strip()
        field = line.split("\t")
        tank = field[0]
        if field[1] == '0':
            # LOGGER.warning("Tank %s is not active", tank)
            continue
        if tank == '(null)':
            # LOGGER.warning("Tank name is null")
            continue
        userid = field[-1]
        maleid = field[-2]
        femaleid = field[-3]
        if maleid == '(null)' and femaleid == '(null)':
            LOGGER.warning("No stock ID for tank %s", tank)
            continue
        if userid in userdict:
            birth = field[2].split(' ')[0]
            stockid = femaleid if femaleid != '(null)' else maleid
            output.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (stockid, tank, userdict[userid],
                                                           str(int(field[3]) + int(field[4])),
                                                           field[3], field[4], birth))
            LOGGER.info(tank)
        else:
            LOGGER.critical("Could not find user %s", userid)
            sys.exit(-1)
    input.close()
    output.close()


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Create new PyRAT files')
    PARSER.add_argument('--verbose', action='store_true',
                        dest='VERBOSE', default=False,
                        help='Turn on verbose output')
    PARSER.add_argument('--debug', action='store_true',
                        dest='DEBUG', default=False,
                        help='Turn on debug output')
    ARG = PARSER.parse_args()

    LOGGER = colorlog.getLogger()
    if ARG.DEBUG:
        LOGGER.setLevel(colorlog.colorlog.logging.DEBUG)
    elif ARG.VERBOSE:
        LOGGER.setLevel(colorlog.colorlog.logging.INFO)
    else:
        LOGGER.setLevel(colorlog.colorlog.logging.WARNING)
    HANDLER = colorlog.StreamHandler()
    HANDLER.setFormatter(colorlog.ColoredFormatter())
    LOGGER.addHandler(HANDLER)

    CONFIG = call_responder('config', 'config/rest_services')['config']
    process_users()
    userdict = create_user_dict()
    process_stocks()
    process_tanks()
    sys.exit(0)
