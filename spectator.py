import configparser
import rospy
import typing as tp
from std_msgs.msg import String
from substrateinterface import *
import configparser
import ast

def substrate_connection(url: str) -> tp.Any:
    """
    establish connection to a specified substrate node
    """
    try:
        rospy.loginfo("Establishing connection to substrate node")
        substrate = SubstrateInterface(
            url=url,
            ss58_format=32,
            type_registry_preset="substrate-node-template",
            type_registry={
                "types": {
                    "<T as frame_system::Config>::AccountId": "AccountId"
                }
            },
        )
        rospy.loginfo("Successfully established connection to substrate node")
        return substrate

    except Exception as e:
        rospy.logerr(f"Failed to connect to substrate: {e}")
        return None

def check_values(substrate):
    """
        checks balances on all the accounts retrieved from config and writes values in accounts dict
    """
    try:
        for account, account_info in substrate.query_map('System', 'Account', max_results=199):
            if account.value in accounts:
                accounts[account.value] = account_info.value['data']['free']

    except Exception as e:
        rospy.logerr(f"Problem retrieving info from substrate: {e}")
        substrate_connection(node_address)


if __name__ == '__main__':

    rospy.init_node('spectator', anonymous=False)
    rospy.loginfo("Node initialized")
    pub = rospy.Publisher('spectator', String, queue_size=10)
    rate = rospy.Rate(0.1)  # 0.1hz

    config = configparser.ConfigParser()
    config.read('config.config')
    node_address = config.get('keys_and_addresses', 'NODE_ADDRESS')
    accounts = dict.fromkeys(ast.literal_eval(config.get("addresses", "accounts")))

    substrate = substrate_connection(node_address)

    while not rospy.is_shutdown():
        check_values(substrate)
        c = 0
        for i in accounts.values():
            pub.publish(f"P{c} = '{i / sum(accounts.values())}'")
            c+=1
        rate.sleep()