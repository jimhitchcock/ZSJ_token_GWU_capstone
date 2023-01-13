import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

#Created a contract helper function to load the function and connect the contract using the abi address
@st.cache(allow_output_mutation=True)
def load_contract():
    with open(Path('./compiled/propertyrecord_abi.json')) as f:
        propertywork_abi = json.load(f)
       
        contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

        contract = w3.eth.contract(
            address=contract_address,
            abi=propertywork_abi 
        )

        return contract

contract = load_contract()

#Helper function to pin property to IPFS
def pin_propertywork(propertywork_name, propertywork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(propertywork_file.getvalue())

    # Build a metadata file for the property
    token_json = {
        "name": propertywork_name,
        "image": ipfs_file_hash
    }
    # Convert the metadata to the JSON data string that Pinata requires
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash

def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash

st.title("Property Record Appraisal System")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

# Register New Property
################################################################################
st.markdown("## Register Initial Purchase of Property")
propertywork_name = st.text_input("Enter the name of the Property")
property_name = st.text_input("Enter the property address")
initial_appraisal_value = st.text_input("Enter the initial property amount")
file = st.file_uploader("Upload Property", type=["jpg", "jpeg", "png", "doc", "pdf"])
if st.button("Register Property"):
    # Use the `pin_artwork` helper function to pin the file to IPFS
    propertywork_ipfs_hash = pin_propertywork(propertywork_name, file)
    propertywork_uri = f"ipfs://{propertywork_ipfs_hash}"
    tx_hash = contract.functions.registerpropertywork(
        address,
        propertywork_name,
        property_name,
        int(initial_appraisal_value),
        propertywork_uri
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Property IPFS Gateway Link](https://ipfs.io/ipfs/{propertywork_ipfs_hash})")
st.markdown("---")

# Appraise Property
################################################################################
st.markdown("## Appraise Property")
tokens = contract.functions.totalSupply().call()
token_id = st.selectbox("Choose an Property Token ID", list(range(tokens)))
new_appraisal_value = st.text_input("Enter the new appraisal amount")
appraisal_report_content = st.text_area("Enter details for the Appraisal Report")
if st.button("Appraise Property"):

    # Use the `pin_appraisal_report` helper function
    # to pin an appraisal report for the report URI
    appraisal_report_ipfs_hash =  pin_appraisal_report(appraisal_report_content)
    report_uri = f"ipfs://{appraisal_report_ipfs_hash}"

    # Use the token_id and the report_uri to record the appraisal
    tx_hash = contract.functions.newAppraisal(
        token_id,
        int(new_appraisal_value),
        report_uri
    ).transact({"from": w3.eth.accounts[0]})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write(receipt)
st.markdown("---")

# Get Appraisals
################################################################################
st.markdown("## Get the appraisal report history")
property_token_id = st.number_input("Property ID", value=0, step=1)
if st.button("Get Appraisal Reports"):
    appraisal_filter = contract.events.Appraisal.createFilter(
        fromBlock="0x0", argument_filters={"tokenId": property_token_id}
    )
    reports = appraisal_filter.get_all_entries()
    if reports:
        for report in reports:
            report_dictionary = dict(report)
            st.markdown("### Appraisal Report Event Log")
            st.write(report_dictionary)
            st.markdown("### Pinata IPFS Report URI")
            report_uri = report_dictionary["args"]["reportURI"]
            report_ipfs_hash = report_uri[7:]
            st.markdown(
                f"The report is located at the following URI: "
                f"{report_uri}"
            )
            st.write("You can also view the report URI with the following ipfs gateway link")
            st.markdown(f"[IPFS Gateway Link](https://ipfs.io/ipfs/{report_ipfs_hash})")
            st.markdown("### Appraisal Event Details")
            st.write(report_dictionary["args"])
    else:
        st.write("This property has no new appraisals")
