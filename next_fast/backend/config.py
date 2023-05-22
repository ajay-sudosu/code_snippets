import json
import boto3
from botocore.exceptions import ClientError
from environs import Env

env = Env()
env.read_env()

is_prod = env.bool("IS_PROD", False)
ENV = env.str("ENV", "DEV")


def get_secrets():
    secret_name = "NEXT_MED_CREDS_" + ENV
    region_name = "us-east-2"

    # Create a Secrets Manager client
    aws_access_key_id = env.str("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = env.str("AWS_SECRET_ACCESS_KEY", "")
    if aws_access_key_id and aws_secret_access_key:
        session = boto3.session.Session(
            aws_access_key_id='',
            aws_secret_access_key=''
        )
    else:
        session = boto3.session.Session()

    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        secret_response = client.get_secret_value(SecretId=secret_name)
        return json.loads(secret_response['SecretString'])
    except ClientError as e:
        raise e


SECRETS = get_secrets()

if not is_prod:
    ADMIN_EMAIL = "nand@joinnextmed.com"
else:
    ADMIN_EMAIL = "rob@joinnextmed.com"

DEFAULT_NURSE_EMAIL = "natasha@joinnextmed.com"

DB_ENDPOINT = SECRETS["DB_ENDPOINT"]
DB_USERNAME = SECRETS["DB_USERNAME"]
DB_PASSWORD = SECRETS["DB_PASSWORD"]
DB_NAME = SECRETS["DB_NAME"]
STRIPE_API_KEY = SECRETS["STRIPE_API_KEY"]
GOOGLE_MAPS_API_KEY = SECRETS["GOOGLE_MAPS_API_KEY"]
TWILIO_ACCOUNT_SID = SECRETS["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = SECRETS["TWILIO_AUTH_TOKEN"]
PLAID_CLIENT_ID = SECRETS["PLAID_CLIENT_ID"]
PLAID_SECRET = SECRETS["PLAID_SECRET"]
DR_CHRONO_CLIENT_ID = SECRETS["DR_CHRONO_CLIENT_ID"]
DR_CHRONO_CLIENT_SECRET = SECRETS["DR_CHRONO_CLIENT_SECRET"]
HEALTHIE_API_KEY = SECRETS['HEALTHIE_API_KEY']
HEALTHIE_API_URL = SECRETS['HEALTHIE_API_URL']
JWT_SECRET = SECRETS['JWT_SECRET']
JWT_ALGORITHM = SECRETS['JWT_ALGORITHM']
CMM_USERNAME = SECRETS['CMM_USERNAME']
CMM_PASSWORD = SECRETS['CMM_PASSWORD']
HUMHEALTH_USERNAME = SECRETS['HUMHEALTH_USERNAME']
HUMHEALTH_PASSWORD = SECRETS['HUMHEALTH_PASSWORD']
HUMHEALTH_HOST =  SECRETS['HUMHEALTH_HOST']
AWS_ACCESS_KEY_ID = SECRETS['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = SECRETS['AWS_SECRET_ACCESS_KEY']
PLAID_ENV = 'sandbox'
PLAID_PRODUCTS = 'transactions'
PLAID_COUNTRY_CODES = 'US'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

TEST_CODES = {
    'STD Standard': ['P03^GC/CHLAM/TRICH/MG', '327^HIV 1,2 AG/AB, 4TH GENERATION (SCREEN)', '1048^SYPHILIS IGG'],
    'STD Complete': ['P03^GC/CHLAM/TRICH/MG', '327^HIV 1,2 AG/AB, 4TH GENERATION (SCREEN)', '1048^SYPHILIS IGG',
                     'P242^BACTERIAL VAGINOSIS/VAGINITIS PNL DNA PRB', '328^HERPES SIMPLEX VIRUS-1 IgG',
                     '329^HERPES SIMPLEX VIRUS-2 IgG', 'P260^CULTURE, MYCOPLASMA HOMINIS / UREAPLASMA',
                     '339^HEPATITIS BS AG QUAL'],
    'Heart Health Test': ['P70^LIPID PANEL W/RFX TO DIRECT LDL', '352^C-REACTIVE PROTEIN, HIGH SENSITIVITY',
                          '82^HEMOGLOBIN A1C'],
    'Heavy Metals Test ': ['P1814^HEAVY METALS PANEL'],
    'Lyme Disease Test': ['330^LYME TOTAL IGG/IGM W/FRX TO WESTERN BLOT'],
    'Vitamin B': ['4055^VITAMIN B1 (THIAMINE)', '4056^VITAMIN B2 (RIBOFLAVIN)', '4057^VITAMIN B3 (NIACIN)',
                  '4058^VITAMIN B5 (PANTOTHENIC ACID)', '4059^VITAMIN B6 SERUM', '4061^VITAMIN B7 (BIOTIN)'],
    'Vitamin D & Inflammation': ['4052^VITAMIN 25OH-D [D2, D3] LCMS', '352^C-REACTIVE PROTEIN, HIGH SENSITIVITY'],
    'Thyroid & Metabolism': ['P8^THYROID PANEL', '303^CORTISOL TOTAL, SERUM'],
    'Women’s Health': ['104^ESTRADIOL-E2', '103^PROGESTERONE', '101^LH (LUTEINIZING HORMONE)',
                       '100^FSH(FOLLICLE STIMULATING HORMONE)', '115^DHEA SULFATE', '303^CORTISOL TOTAL, SERUM',
                       '1660^THYROID CASCADE PROFILE', '112^T3 FREE TRIIODOTHYRONINE', '111^T4 FREE, THYROXINE',
                       '106^TESTOSTERONE TOTAL', '317^THYROID PEROXIDASE ANTIBO'],
    'Men’s Health': ['303^CORTISOL TOTAL, SERUM', '115^DHEA SULFATE', '104^ESTRADIOL-E2',
                     'P184^TESTOSTERONE FREE & TOTAL'],
    'Indoor/Outdoor Allergy': ['P186^RESPIRAT. ALLERGY + IGE'],
    '36 Food Allergy Panel Test': ['P187^36 Food Allergy Panel PANEL', '1098^PEACH (F95) IGE', '1101^BANANA (F92) IGE',
                                   '1358^AVOCADO (F96) IGE', '2017^KIWI FRUIT (F84) IGE', '1602^CELERY (F85) IGE',
                                   '1357^GARLIC(F47)IGE', '1606^MUSTARD (F89) IGE', '2280^GELATIN IGE',
                                   '1169^BEEF (F27) IGE', '893^CHICKEN MEAT (F83) IGE', '1170^PORK (F26) IGE',
                                   '1842^CORIANDER / CILANTRO (F317) IGE', '1172^RICE (F9) IGE',
                                   '2016^MANGO FRUIT (F91) IGE', '1109^STRAWBERRY (F44) IGE',
                                   '1108^PINEAPPPLE (F210) IGE', '1096^APPLE (F49) IGE', '1173^TOMATO (F25) IGE',
                                   '1168^SQUID (F258) IGE', '1110^WATERMELON (RF329) IGE'],
    'Women’s Fertility Test': ['104^ESTRADIOL-E2', '101^LH (LUTEINIZING HORMONE)', '100^FSH(FOLLICLE STIMULATING',
                               '1660^THYROID CASCADE PROFILE', '106^TESTOSTERONE TOTAL'],
    'Celiac Complete Test': ['P863^Celiac Complete: TTG (IGG, IGA) + GLIADIN (IGA, IGG)'],
    'Anemia': ['P275^ANEMIA PANEL'],
    'Vitamins Panel': ['P1815^ FULL VITAMINS PANEL'],
    'Gastrointestinal Distress': ['P861^GASTROINTESTINAL(GI) DISTRESS PROFILE', 'P1988^BIOFIRE, GI PATHOGENS PANEL'],
    'Arthritis Test': ['P274^ARTHRITIS PANEL'],
    'Diabetes': ['P811^DIABETES PROFILE'],
    'Immune Defense': ['494^GLUCOSE, PLASMA', '352^C-REACTIVE PROTEIN, HIGH SENSITIVITY', '829^VITAMIN D 25-HYDROXY',
                       '82^HEMOGLOBIN A1C'],
    'Male Hormone Standard': ['106^TESTOSTERONE TOTAL'],
    'PCR': ['8800^2019 Novel Coronavirus (COVID-19) RNA, QL RT-PCR'],
    'Antibody': ['5643^SARS-COV-2, Total Antibodies, IGG/IGM'],
    'Urinary Tract': ['P52^URINALYSIS COMPLETE W/RFX CULTURE']
}


def get_aws_sns_client():
    """Return boto3 SNS client"""
    aws_sns_client = boto3.client(
        "sns",
        aws_access_key_id=env.str("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=env.str("AWS_SECRET_ACCESS_KEY", ""),
        region_name="us-east-1"
    )
    return aws_sns_client


def get_mdintegration_case_complete(name, drname="John Doe", photourl="https://picsum.photos/id/237/200/300"):
    k = """<table cellpadding="0" cellspacing="0" width="100%" align="center" style="font-family:jost,sans-serif">
    <tr>
        <td valign="top">
            <table cellpadding="0" cellspacing="0" width="718" align="center">
                <tr>
                    <td width="18"></td>
                    <td width="598" style="background-color:#ffffff; padding:30px 42px;border:2px solid #80808036;"
                        valign="top">
                        <table cellpadding="0" cellspacing="0" width="100%" style="padding: 10px;">
                            <tr>
                                <td align="center"
                                    style="color:#1c5bb9; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                    Hi """ + name + """,
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td align="center"
                                    style="color:#000000; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                   Your test has been approved by """ + drname + """.
                                </td>
                            </tr>
                            <tr>
                                <td align="center" valign="top" style="padding:20px;">
                                    <a href="#" style="color:#fff;font-size:30px;text-decoration:none;">
                                        <img src=""" + photourl + """
                                            alt="logo" style="border-radius: 50%;width: 160px;
                                            height: 160px; object-fit: cover;" /></a>
                                </td>
                            </tr>
                            <tr>
                                <td valign="top" style="padding:15px;"></td>
                            </tr>
                            <tr>
                                <td align="center">
                                    <a href="https://joinnextmedical.com/visits" style="color: #fff;
                                        font-size: 18px;
                                        text-decoration: none;
                                        background-color: #1c5bb9;
                                        padding: 15px 80px;
                                        border-radius: 35px;">
                                    Download Script
                                    </a>
                                </td>
                            </tr>

                            <tr >
                                <td style="padding-top:60px;"></td>
                            </tr>
                            
                        </table>
                    </td>
                    <td width="18">
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>"""
    return k


def get_mdintegration_case_results_upload(name, drname="John Doe", photourl="https://picsum.photos/id/237/200/300"):
    k = """<table cellpadding="0" cellspacing="0" width="100%" align="center" style="font-family:jost,sans-serif">
    <tr>
        <td valign="top">
            <table cellpadding="0" cellspacing="0" width="718" align="center">
                <tr>
                    <td width="18"></td>
                    <td width="598" style="background-color:#ffffff; padding:30px 42px;border:2px solid #80808036;"
                        valign="top">
                        <table cellpadding="0" cellspacing="0" width="100%" style="padding: 10px;">
                            <tr>
                                <td align="center"
                                    style="color:#1c5bb9; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                    Hi """ + name + """,
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td align="center"
                                    style="color:#000000; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                   Your results are now ready to review from your Next Medical Appointment. 
                                </td>
                            </tr>
                            <tr>
                                <td valign="top" style="padding:15px;"></td>
                            </tr>
                            <tr>
                                <td align="center">
                                    <a href="https://joinnextmed.com/visits" style="color: #fff;
                                        font-size: 18px;
                                        text-decoration: none;
                                        background-color: #1c5bb9;
                                        padding: 15px 80px;
                                        border-radius: 35px;">
                                    View Results
                                    </a>
                                </td>
                            </tr>

                            <tr >
                                <td style="padding-top:60px;"></td>
                            </tr>
                            
                        </table>
                    </td>
                    <td width="18">
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>"""
    return k


def get_drchrono_add(data):
    k = """<table cellpadding="0" cellspacing="0" width="100%" align="center" style="font-family:jost,sans-serif">
    <tr>
        <td valign="top">
            <table cellpadding="0" cellspacing="0" width="718" align="center">
                <tr>
                    <td width="18"></td>
                    <td width="598" style="background-color:#ffffff; padding:30px 42px;border:2px solid #80808036;"
                        valign="top">
                        <table cellpadding="0" cellspacing="0" width="100%" style="padding: 10px;">
                            <tr>
                                <td align="center"
                                    style="color:#1c5bb9; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                    Hi """ + "Team" + """,
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td align="center"
                                    style="color:#000000; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                  For Drchrono add Patient Data ,<br>
                                  Patient Name = """ + data["first_name"] + " " + data["last_name"] + """ ,<br>
                                  Email = """ + data["email"] + """, <br>
                                  Gender = """ + data["gender"] + """ ,<br>
                                  Phone No. = """ + data["phone"] + """ ,<br>
                                  zip_code = """ + data["zip_code"] + """ ,<br>
                                  date_of_birth = """ + data["date_of_birth"] + """,<br> 
                                  address = """ + data["address"] + """ ,<br>
                                  city = """ + data["city"] + """ ,<br>
                                  state = """ + data["state"] + """ ,<br>
                                  insurance_company = """ + data["insurance_company"] + """ ,<br>
                                  insurance_id = """ + data["insurance_id"] + """ ,<br>
                                  insurance_group = """ + data["insurance_group"] + """ ,<br>
                                </td>
                            </tr>
                            <tr>
                                <td valign="top" style="padding:15px;"></td>
                            </tr>
                           

                            <tr >
                                <td style="padding-top:60px;"></td>
                            </tr>
                            
                        </table>
                    </td>
                    <td width="18">
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>"""
    return k


def get_mdintegration_case_message(name, drname="John Doe", photourl="https://picsum.photos/id/237/200/300"):
    k = """<table cellpadding="0" cellspacing="0" width="100%" align="center" style="font-family:jost,sans-serif">
    <tr>
        <td valign="top">
            <table cellpadding="0" cellspacing="0" width="718" align="center">
                <tr>
                    <td width="18"></td>
                    <td width="598" style="background-color:#ffffff; padding:30px 42px;border:2px solid #80808036;"
                        valign="top">
                        <table cellpadding="0" cellspacing="0" width="100%" style="padding: 10px;">
                            <tr>
                                <td align="center" valign="top" style="padding:20px;">
                                    <a href="https://www.joinnextmed.com/" style="color:#fff;font-size:30px;text-decoration:none;">
                                        <img src="https://www.joinnextmed.com/images/logo.png"
                                            alt="logo" style="width: 150px;
                                            height: 50px; object-fit: cover;" /></a>
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td align="center"
                                    style="color:#1c5bb9; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                    Hi """ + name + """,
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                            </tr>
                            <tr>
                                <td align="center"
                                    style="color:#000000; font-size:20px; padding:15px 15px 0 15px; line-height: 1.5;font-weight: bold;">
                                   """ + drname + """ has sent a message.
                                </td>
                            </tr>
                            <tr>
                                <td align="center" valign="top" style="padding:20px;">
                                    <a href="#" style="color:#fff;font-size:30px;text-decoration:none;">
                                        <img src=""" + photourl + """
                                            alt="logo" style="border-radius: 50%;width: 160px;
                                            height: 160px; object-fit: cover;" /></a>
                                </td>
                            </tr>
                            <tr>
                                <td valign="top" style="padding:15px;"></td>
                            </tr>
                            <tr>
                                <td align="center">
                                    <a href="https://joinnextmed.com/messages" style="color: #fff;
                                        font-size: 18px;
                                        text-decoration: none;
                                        background-color: #1c5bb9;
                                        padding: 15px 80px;
                                        border-radius: 35px;">
                                    Respond Now
                                    </a>
                                </td>
                            </tr>

                            <tr >
                                <td style="padding-top:60px;"></td>
                            </tr>
                            
                        </table>
                    </td>
                    <td width="18">
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>"""
    return k


def get_html_on_the_way(name, mrn):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px">
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Your Next Medical Medical Assistant is on the way to your home. You can track the visit live <a href="https://joinnextmed.com/track?mrn=""" + mrn + """">here</a>.</p></td> 
                     </tr> 
                     
                     
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
    return k


def get_html_doctor_note(name):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px">
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Your Next Medical doctor has reviewed your test results and posted a doctor's note to your portal. Please login <a href="https://joinnextmed.com/login">here</a> to view the note.</p></td> 
                     </tr> 
                     
                     
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
    return k


def get_html_refunded(name, date):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px">
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Thank you for choosing Next Medical. Your visit scheduled for """ + date + """ has been refunded.</p></td> 
                     </tr> 
                     
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
    return k


def get_html_patient_feedback(recommend, alternative, comments, future_tests):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  style="
    width: 100%;
    font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    padding: 0;
    margin: 0;
  "
>
  <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta content="telephone=no" name="format-detection" />
    <title>New Template</title>
    <script>
      function myFunction() {
        var copyText = document.getElementById("myAnchor").textContent;
        document.addEventListener(
          "copy",
          function (event) {
            event.clipboardData.setData("text/plain", copyText);
            event.preventDefault();
            document.removeEventListener("copy", handler, true);
          },
          true
        );
        document.execCommand("copy");
        // alert("Copied: " + copyText);
      }
      document.getElementById("myAnchor").addEventListener("click", myFunction);
    </script>
    <!--[if (mso 16)]>
      <style type="text/css">
        a {
          text-decoration: none;
        }
      </style>
    <![endif]-->
    <!--[if gte mso 9
      ]><style>
        sup {
          font-size: 100% !important;
        }
      </style><!
    [endif]-->
    <!--[if gte mso 9]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG></o:AllowPNG>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
    <![endif]-->
    <!--[if !mso]><!-- -->
    <link
      href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i"
      rel="stylesheet"
    />
    <!--<![endif]-->
    <style type="text/css">
      #outlook a {
        padding: 0;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .es-button {
        mso-style-priority: 100 !important;
        text-decoration: none !important;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      .es-desk-hidden {
        display: none;
        float: left;
        overflow: hidden;
        width: 0;
        max-height: 0;
        line-height: 0;
        mso-hide: all;
      }
      @media only screen and (max-width: 600px) {
        p,
        ul li,
        ol li,
        a {
          font-size: 16px !important;
          line-height: 150% !important;
        }
        h1 {
          font-size: 30px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h2 {
          font-size: 26px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h3 {
          font-size: 20px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h1 a {
          font-size: 30px !important;
        }
        h2 a {
          font-size: 26px !important;
        }
        h3 a {
          font-size: 20px !important;
        }
        .es-menu td a {
          font-size: 16px !important;
        }
        .es-header-body p,
        .es-header-body ul li,
        .es-header-body ol li,
        .es-header-body a {
          font-size: 16px !important;
        }
        .es-footer-body p,
        .es-footer-body ul li,
        .es-footer-body ol li,
        .es-footer-body a {
          font-size: 16px !important;
        }
        .es-infoblock p,
        .es-infoblock ul li,
        .es-infoblock ol li,
        .es-infoblock a {
          font-size: 12px !important;
        }
        *[class="gmail-fix"] {
          display: none !important;
        }
        .es-m-txt-c,
        .es-m-txt-c h1,
        .es-m-txt-c h2,
        .es-m-txt-c h3 {
          text-align: center !important;
        }
        .es-m-txt-r,
        .es-m-txt-r h1,
        .es-m-txt-r h2,
        .es-m-txt-r h3 {
          text-align: right !important;
        }
        .es-m-txt-l,
        .es-m-txt-l h1,
        .es-m-txt-l h2,
        .es-m-txt-l h3 {
          text-align: left !important;
        }
        .es-m-txt-r img,
        .es-m-txt-c img,
        .es-m-txt-l img {
          display: inline !important;
        }
        .es-button-border {
          display: block !important;
        }
        .es-btn-fw {
          border-width: 10px 0px !important;
          text-align: center !important;
        }
        .es-adaptive table,
        .es-btn-fw,
        .es-btn-fw-brdr,
        .es-left,
        .es-right {
          width: 100% !important;
        }
        .es-content table,
        .es-header table,
        .es-footer table,
        .es-content,
        .es-footer,
        .es-header {
          width: 100% !important;
          max-width: 600px !important;
        }
        .es-adapt-td {
          display: block !important;
          width: 100% !important;
        }
        .adapt-img {
          width: 100% !important;
          height: auto !important;
        }
        .es-m-p0 {
          padding: 0px !important;
        }
        .es-m-p0r {
          padding-right: 0px !important;
        }
        .es-m-p0l {
          padding-left: 0px !important;
        }
        .es-m-p0t {
          padding-top: 0px !important;
        }
        .es-m-p0b {
          padding-bottom: 0 !important;
        }
        .es-m-p20b {
          padding-bottom: 20px !important;
        }
        .es-mobile-hidden,
        .es-hidden {
          display: none !important;
        }
        tr.es-desk-hidden,
        td.es-desk-hidden,
        table.es-desk-hidden {
          width: auto !important;
          overflow: visible !important;
          float: none !important;
          max-height: inherit !important;
          line-height: inherit !important;
        }
        tr.es-desk-hidden {
          display: table-row !important;
        }
        table.es-desk-hidden {
          display: table !important;
        }
        td.es-desk-menu-hidden {
          display: table-cell !important;
        }
        .es-menu td {
          width: 1% !important;
        }
        table.es-table-not-adapt,
        .esd-block-html table {
          width: auto !important;
        }
        table.es-social {
          display: inline-block !important;
        }
        table.es-social td {
          display: inline-block !important;
        }
        a.es-button,
        button.es-button {
          font-size: 20px !important;
          display: block !important;
          border-width: 15px 25px 15px 25px !important;
        }
      }
    </style>
  </head>
  <body
    style="
      width: 100%;
      font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
      padding: 0;
      margin: 0;
    "
  >
    <div class="es-wrapper-color" style="background-color: #f4f4f4">
      <!--[if gte mso 9]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
          <v:fill type="tile" color="#f4f4f4"></v:fill>
        </v:background>
      <![endif]-->
      <table
        class="es-wrapper"
        width="100%"
        cellspacing="0"
        cellpadding="0"
        style="
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          border-collapse: collapse;
          border-spacing: 0px;
          padding: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          background-repeat: repeat;
          background-position: center top;
        "
      >
        <tr class="gmail-fix" height="0" style="border-collapse: collapse">
          <td style="padding: 0; margin: 0">
            <table
              cellspacing="0"
              cellpadding="0"
              border="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                width: 600px;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  cellpadding="0"
                  cellspacing="0"
                  border="0"
                  style="
                    padding: 0;
                    margin: 0;
                    line-height: 1px;
                    min-width: 600px;
                  "
                  height="0"
                >
                  <img
                    src="https://esputnik.com/repository/applications/images/blank.gif"
                    style="
                      display: block;
                      border: 0;
                      outline: none;
                      text-decoration: none;
                      -ms-interpolation-mode: bicubic;
                      max-height: 0px;
                      min-height: 0px;
                      min-width: 600px;
                      width: 600px;
                    "
                    alt
                    width="600"
                    height="1"
                  />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr style="border-collapse: collapse">
          <td valign="top" style="padding: 0; margin: 0">
            <table
              class="es-header"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
                background-repeat: repeat;
                background-position: center top;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  align="center"
                  bgcolor="#f4f4f4"
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                >
                  <table
                    class="es-header-body"
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                  >
                    <tr style="border-collapse: collapse">
                      <td
                        align="left"
                        style="
                          margin: 0;
                          padding-bottom: 10px;
                          padding-left: 10px;
                          padding-right: 10px;
                          padding-top: 20px;
                        "
                      >
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 580px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-left: 10px;
                                      padding-right: 10px;
                                      padding-top: 25px;
                                      padding-bottom: 25px;
                                      font-size: 0px;
                                    "
                                  >
                                    <img
                                      src="https://www.joinnextmed.com/images/logo.png"
                                      alt
                                      style="
                                        display: block;
                                        border: 0;
                                        outline: none;
                                        text-decoration: none;
                                        -ms-interpolation-mode: bicubic;
                                      "
                                      width="215"
                                    />
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                  bgcolor="#f4f4f4"
                  align="center"
                >
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: #0d55b0;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  background-color: #ffffff;
                                  border-radius: 4px;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    bgcolor="#ffffff"
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 5px;
                                      padding-bottom: 5px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <td
                                          style="
                                            padding: 0;
                                            margin: 0;
                                            border-bottom: 1px solid #ffffff;
                                            background: #ffffff none repeat
                                              scroll 0% 0%;
                                            height: 1px;
                                            width: 100%;
                                            margin: 0px;
                                          "
                                        ></td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  border-radius: 4px;
                                  background-color: #ffffff;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        color: #666666;
                                      "
                                    >
New Review                                    </p>
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    How likely patient recommend Next Medical to
                                    a friend!<br />
                                    """ + recommend + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    If Next Medical was not available, here
                                    patient have gone!<br />
                                     """ + alternative + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Which health tests would patient like us to
                                    add in the future!<br />
                                     """ + future_tests + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Patient like to tell us!<br />
                                     """ + comments + """
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 0px;
                                      padding-bottom: 0px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  ></td>
                                </tr>
                                <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#f4f4f4;background:#f4f4f4;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#f4f4f4;border-width:15px 30px;display:inline-block;background:#f4f4f4;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#f4f4f4">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                      padding-bottom: 40px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      Cheers,
                                    </p>
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      The Next Medical&nbsp;Team
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 20px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>

"""
    return k


def get_html_patient_failed_laborder():
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  style="
    width: 100%;
    font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    padding: 0;
    margin: 0;
  "
>
  <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta content="telephone=no" name="format-detection" />
    <title>New Template</title>
    <script>
      function myFunction() {
        var copyText = document.getElementById("myAnchor").textContent;
        document.addEventListener(
          "copy",
          function (event) {
            event.clipboardData.setData("text/plain", copyText);
            event.preventDefault();
            document.removeEventListener("copy", handler, true);
          },
          true
        );
        document.execCommand("copy");
        // alert("Copied: " + copyText);
      }
      document.getElementById("myAnchor").addEventListener("click", myFunction);
    </script>
    <!--[if (mso 16)]>
      <style type="text/css">
        a {
          text-decoration: none;
        }
      </style>
    <![endif]-->
    <!--[if gte mso 9
      ]><style>
        sup {
          font-size: 100% !important;
        }
      </style><!
    [endif]-->
    <!--[if gte mso 9]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG></o:AllowPNG>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
    <![endif]-->
    <!--[if !mso]><!-- -->
    <link
      href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i"
      rel="stylesheet"
    />
    <!--<![endif]-->
    <style type="text/css">
      #outlook a {
        padding: 0;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .es-button {
        mso-style-priority: 100 !important;
        text-decoration: none !important;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      .es-desk-hidden {
        display: none;
        float: left;
        overflow: hidden;
        width: 0;
        max-height: 0;
        line-height: 0;
        mso-hide: all;
      }
      @media only screen and (max-width: 600px) {
        p,
        ul li,
        ol li,
        a {
          font-size: 16px !important;
          line-height: 150% !important;
        }
        h1 {
          font-size: 30px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h2 {
          font-size: 26px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h3 {
          font-size: 20px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h1 a {
          font-size: 30px !important;
        }
        h2 a {
          font-size: 26px !important;
        }
        h3 a {
          font-size: 20px !important;
        }
        .es-menu td a {
          font-size: 16px !important;
        }
        .es-header-body p,
        .es-header-body ul li,
        .es-header-body ol li,
        .es-header-body a {
          font-size: 16px !important;
        }
        .es-footer-body p,
        .es-footer-body ul li,
        .es-footer-body ol li,
        .es-footer-body a {
          font-size: 16px !important;
        }
        .es-infoblock p,
        .es-infoblock ul li,
        .es-infoblock ol li,
        .es-infoblock a {
          font-size: 12px !important;
        }
        *[class="gmail-fix"] {
          display: none !important;
        }
        .es-m-txt-c,
        .es-m-txt-c h1,
        .es-m-txt-c h2,
        .es-m-txt-c h3 {
          text-align: center !important;
        }
        .es-m-txt-r,
        .es-m-txt-r h1,
        .es-m-txt-r h2,
        .es-m-txt-r h3 {
          text-align: right !important;
        }
        .es-m-txt-l,
        .es-m-txt-l h1,
        .es-m-txt-l h2,
        .es-m-txt-l h3 {
          text-align: left !important;
        }
        .es-m-txt-r img,
        .es-m-txt-c img,
        .es-m-txt-l img {
          display: inline !important;
        }
        .es-button-border {
          display: block !important;
        }
        .es-btn-fw {
          border-width: 10px 0px !important;
          text-align: center !important;
        }
        .es-adaptive table,
        .es-btn-fw,
        .es-btn-fw-brdr,
        .es-left,
        .es-right {
          width: 100% !important;
        }
        .es-content table,
        .es-header table,
        .es-footer table,
        .es-content,
        .es-footer,
        .es-header {
          width: 100% !important;
          max-width: 600px !important;
        }
        .es-adapt-td {
          display: block !important;
          width: 100% !important;
        }
        .adapt-img {
          width: 100% !important;
          height: auto !important;
        }
        .es-m-p0 {
          padding: 0px !important;
        }
        .es-m-p0r {
          padding-right: 0px !important;
        }
        .es-m-p0l {
          padding-left: 0px !important;
        }
        .es-m-p0t {
          padding-top: 0px !important;
        }
        .es-m-p0b {
          padding-bottom: 0 !important;
        }
        .es-m-p20b {
          padding-bottom: 20px !important;
        }
        .es-mobile-hidden,
        .es-hidden {
          display: none !important;
        }
        tr.es-desk-hidden,
        td.es-desk-hidden,
        table.es-desk-hidden {
          width: auto !important;
          overflow: visible !important;
          float: none !important;
          max-height: inherit !important;
          line-height: inherit !important;
        }
        tr.es-desk-hidden {
          display: table-row !important;
        }
        table.es-desk-hidden {
          display: table !important;
        }
        td.es-desk-menu-hidden {
          display: table-cell !important;
        }
        .es-menu td {
          width: 1% !important;
        }
        table.es-table-not-adapt,
        .esd-block-html table {
          width: auto !important;
        }
        table.es-social {
          display: inline-block !important;
        }
        table.es-social td {
          display: inline-block !important;
        }
        a.es-button,
        button.es-button {
          font-size: 20px !important;
          display: block !important;
          border-width: 15px 25px 15px 25px !important;
        }
      }
    </style>
  </head>
  <body
    style="
      width: 100%;
      font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
      padding: 0;
      margin: 0;
    "
  >
    <div class="es-wrapper-color" style="background-color: #f4f4f4">
      <!--[if gte mso 9]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
          <v:fill type="tile" color="#f4f4f4"></v:fill>
        </v:background>
      <![endif]-->
      <table
        class="es-wrapper"
        width="100%"
        cellspacing="0"
        cellpadding="0"
        style="
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          border-collapse: collapse;
          border-spacing: 0px;
          padding: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          background-repeat: repeat;
          background-position: center top;
        "
      >
        <tr class="gmail-fix" height="0" style="border-collapse: collapse">
          <td style="padding: 0; margin: 0">
            <table
              cellspacing="0"
              cellpadding="0"
              border="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                width: 600px;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  cellpadding="0"
                  cellspacing="0"
                  border="0"
                  style="
                    padding: 0;
                    margin: 0;
                    line-height: 1px;
                    min-width: 600px;
                  "
                  height="0"
                >
                  <img
                    src="https://esputnik.com/repository/applications/images/blank.gif"
                    style="
                      display: block;
                      border: 0;
                      outline: none;
                      text-decoration: none;
                      -ms-interpolation-mode: bicubic;
                      max-height: 0px;
                      min-height: 0px;
                      min-width: 600px;
                      width: 600px;
                    "
                    alt
                    width="600"
                    height="1"
                  />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr style="border-collapse: collapse">
          <td valign="top" style="padding: 0; margin: 0">
            <table
              class="es-header"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
                background-repeat: repeat;
                background-position: center top;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  align="center"
                  bgcolor="#f4f4f4"
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                >
                  <table
                    class="es-header-body"
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                  >
                    <tr style="border-collapse: collapse">
                      <td
                        align="left"
                        style="
                          margin: 0;
                          padding-bottom: 10px;
                          padding-left: 10px;
                          padding-right: 10px;
                          padding-top: 20px;
                        "
                      >
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 580px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-left: 10px;
                                      padding-right: 10px;
                                      padding-top: 25px;
                                      padding-bottom: 25px;
                                      font-size: 0px;
                                    "
                                  >
                                    <img
                                      src="https://www.joinnextmed.com/images/logo.png"
                                      alt
                                      style="
                                        display: block;
                                        border: 0;
                                        outline: none;
                                        text-decoration: none;
                                        -ms-interpolation-mode: bicubic;
                                      "
                                      width="215"
                                    />
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                  bgcolor="#f4f4f4"
                  align="center"
                >
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: #0d55b0;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  background-color: #ffffff;
                                  border-radius: 4px;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    bgcolor="#ffffff"
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 5px;
                                      padding-bottom: 5px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <td
                                          style="
                                            padding: 0;
                                            margin: 0;
                                            border-bottom: 1px solid #ffffff;
                                            background: #ffffff none repeat
                                              scroll 0% 0%;
                                            height: 1px;
                                            width: 100%;
                                            margin: 0px;
                                          "
                                        ></td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  border-radius: 4px;
                                  background-color: #ffffff;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        color: #666666;
                                      "
                                    >
New Review                                    </p>
                                  </td>
                                </tr>

                                

                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 0px;
                                      padding-bottom: 0px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  ></td>
                                </tr>
                                <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#f4f4f4;background:#f4f4f4;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#f4f4f4;border-width:15px 30px;display:inline-block;background:#f4f4f4;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#f4f4f4">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                      padding-bottom: 40px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      Cheers,
                                    </p>
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      The Next Medical&nbsp;Team
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 20px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>

"""
    return k


def get_html_patient_bad_feedback(recommend, alternative, comments, future_tests, name, email, time):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  style="
    width: 100%;
    font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    padding: 0;
    margin: 0;
  "
>
  <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta content="telephone=no" name="format-detection" />
    <title>New Template</title>
    <script>
      function myFunction() {
        var copyText = document.getElementById("myAnchor").textContent;
        document.addEventListener(
          "copy",
          function (event) {
            event.clipboardData.setData("text/plain", copyText);
            event.preventDefault();
            document.removeEventListener("copy", handler, true);
          },
          true
        );
        document.execCommand("copy");
        // alert("Copied: " + copyText);
      }
      document.getElementById("myAnchor").addEventListener("click", myFunction);
    </script>
    <!--[if (mso 16)]>
      <style type="text/css">
        a {
          text-decoration: none;
        }
      </style>
    <![endif]-->
    <!--[if gte mso 9
      ]><style>
        sup {
          font-size: 100% !important;
        }
      </style><!
    [endif]-->
    <!--[if gte mso 9]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG></o:AllowPNG>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
    <![endif]-->
    <!--[if !mso]><!-- -->
    <link
      href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i"
      rel="stylesheet"
    />
    <!--<![endif]-->
    <style type="text/css">
      #outlook a {
        padding: 0;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .es-button {
        mso-style-priority: 100 !important;
        text-decoration: none !important;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      .es-desk-hidden {
        display: none;
        float: left;
        overflow: hidden;
        width: 0;
        max-height: 0;
        line-height: 0;
        mso-hide: all;
      }
      @media only screen and (max-width: 600px) {
        p,
        ul li,
        ol li,
        a {
          font-size: 16px !important;
          line-height: 150% !important;
        }
        h1 {
          font-size: 30px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h2 {
          font-size: 26px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h3 {
          font-size: 20px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h1 a {
          font-size: 30px !important;
        }
        h2 a {
          font-size: 26px !important;
        }
        h3 a {
          font-size: 20px !important;
        }
        .es-menu td a {
          font-size: 16px !important;
        }
        .es-header-body p,
        .es-header-body ul li,
        .es-header-body ol li,
        .es-header-body a {
          font-size: 16px !important;
        }
        .es-footer-body p,
        .es-footer-body ul li,
        .es-footer-body ol li,
        .es-footer-body a {
          font-size: 16px !important;
        }
        .es-infoblock p,
        .es-infoblock ul li,
        .es-infoblock ol li,
        .es-infoblock a {
          font-size: 12px !important;
        }
        *[class="gmail-fix"] {
          display: none !important;
        }
        .es-m-txt-c,
        .es-m-txt-c h1,
        .es-m-txt-c h2,
        .es-m-txt-c h3 {
          text-align: center !important;
        }
        .es-m-txt-r,
        .es-m-txt-r h1,
        .es-m-txt-r h2,
        .es-m-txt-r h3 {
          text-align: right !important;
        }
        .es-m-txt-l,
        .es-m-txt-l h1,
        .es-m-txt-l h2,
        .es-m-txt-l h3 {
          text-align: left !important;
        }
        .es-m-txt-r img,
        .es-m-txt-c img,
        .es-m-txt-l img {
          display: inline !important;
        }
        .es-button-border {
          display: block !important;
        }
        .es-btn-fw {
          border-width: 10px 0px !important;
          text-align: center !important;
        }
        .es-adaptive table,
        .es-btn-fw,
        .es-btn-fw-brdr,
        .es-left,
        .es-right {
          width: 100% !important;
        }
        .es-content table,
        .es-header table,
        .es-footer table,
        .es-content,
        .es-footer,
        .es-header {
          width: 100% !important;
          max-width: 600px !important;
        }
        .es-adapt-td {
          display: block !important;
          width: 100% !important;
        }
        .adapt-img {
          width: 100% !important;
          height: auto !important;
        }
        .es-m-p0 {
          padding: 0px !important;
        }
        .es-m-p0r {
          padding-right: 0px !important;
        }
        .es-m-p0l {
          padding-left: 0px !important;
        }
        .es-m-p0t {
          padding-top: 0px !important;
        }
        .es-m-p0b {
          padding-bottom: 0 !important;
        }
        .es-m-p20b {
          padding-bottom: 20px !important;
        }
        .es-mobile-hidden,
        .es-hidden {
          display: none !important;
        }
        tr.es-desk-hidden,
        td.es-desk-hidden,
        table.es-desk-hidden {
          width: auto !important;
          overflow: visible !important;
          float: none !important;
          max-height: inherit !important;
          line-height: inherit !important;
        }
        tr.es-desk-hidden {
          display: table-row !important;
        }
        table.es-desk-hidden {
          display: table !important;
        }
        td.es-desk-menu-hidden {
          display: table-cell !important;
        }
        .es-menu td {
          width: 1% !important;
        }
        table.es-table-not-adapt,
        .esd-block-html table {
          width: auto !important;
        }
        table.es-social {
          display: inline-block !important;
        }
        table.es-social td {
          display: inline-block !important;
        }
        a.es-button,
        button.es-button {
          font-size: 20px !important;
          display: block !important;
          border-width: 15px 25px 15px 25px !important;
        }
      }
    </style>
  </head>
  <body
    style="
      width: 100%;
      font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
      padding: 0;
      margin: 0;
    "
  >
    <div class="es-wrapper-color" style="background-color: #f4f4f4">
      <!--[if gte mso 9]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
          <v:fill type="tile" color="#f4f4f4"></v:fill>
        </v:background>
      <![endif]-->
      <table
        class="es-wrapper"
        width="100%"
        cellspacing="0"
        cellpadding="0"
        style="
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          border-collapse: collapse;
          border-spacing: 0px;
          padding: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          background-repeat: repeat;
          background-position: center top;
        "
      >
        <tr class="gmail-fix" height="0" style="border-collapse: collapse">
          <td style="padding: 0; margin: 0">
            <table
              cellspacing="0"
              cellpadding="0"
              border="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                width: 600px;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  cellpadding="0"
                  cellspacing="0"
                  border="0"
                  style="
                    padding: 0;
                    margin: 0;
                    line-height: 1px;
                    min-width: 600px;
                  "
                  height="0"
                >
                  <img
                    src="https://esputnik.com/repository/applications/images/blank.gif"
                    style="
                      display: block;
                      border: 0;
                      outline: none;
                      text-decoration: none;
                      -ms-interpolation-mode: bicubic;
                      max-height: 0px;
                      min-height: 0px;
                      min-width: 600px;
                      width: 600px;
                    "
                    alt
                    width="600"
                    height="1"
                  />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr style="border-collapse: collapse">
          <td valign="top" style="padding: 0; margin: 0">
            <table
              class="es-header"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
                background-repeat: repeat;
                background-position: center top;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  align="center"
                  bgcolor="#f4f4f4"
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                >
                  <table
                    class="es-header-body"
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                  >
                    <tr style="border-collapse: collapse">
                      <td
                        align="left"
                        style="
                          margin: 0;
                          padding-bottom: 10px;
                          padding-left: 10px;
                          padding-right: 10px;
                          padding-top: 20px;
                        "
                      >
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 580px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-left: 10px;
                                      padding-right: 10px;
                                      padding-top: 25px;
                                      padding-bottom: 25px;
                                      font-size: 0px;
                                    "
                                  >
                                    <img
                                      src="https://www.joinnextmed.com/images/logo.png"
                                      alt
                                      style="
                                        display: block;
                                        border: 0;
                                        outline: none;
                                        text-decoration: none;
                                        -ms-interpolation-mode: bicubic;
                                      "
                                      width="215"
                                    />
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                  bgcolor="#f4f4f4"
                  align="center"
                >
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: #0d55b0;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  background-color: #ffffff;
                                  border-radius: 4px;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    bgcolor="#ffffff"
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 5px;
                                      padding-bottom: 5px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <td
                                          style="
                                            padding: 0;
                                            margin: 0;
                                            border-bottom: 1px solid #ffffff;
                                            background: #ffffff none repeat
                                              scroll 0% 0%;
                                            height: 1px;
                                            width: 100%;
                                            margin: 0px;
                                          "
                                        ></td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  border-radius: 4px;
                                  background-color: #ffffff;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        color: #666666;
                                      "
                                    >
New Review                                    </p>
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Patient Name :<br />
                                    """ + name + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Patient email:<br />
                                    """ + email + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Feedback Timing: <br />
                                    """ + str(time) + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    How likely patient recommend Next Medical to
                                    a friend!<br />
                                    """ + recommend + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    If Next Medical was not available, here
                                    patient have gone!<br />
                                     """ + alternative + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Which health tests would patient like us to
                                    add in the future!<br />
                                     """ + future_tests + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    Patient like to tell us!<br />
                                     """ + comments + """
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 0px;
                                      padding-bottom: 0px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  ></td>
                                </tr>
                                <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#f4f4f4;background:#f4f4f4;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#f4f4f4;border-width:15px 30px;display:inline-block;background:#f4f4f4;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#f4f4f4">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                      padding-bottom: 40px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      Cheers,
                                    </p>
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      The Next Medical&nbsp;Team
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 20px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>

"""
    return k


def send_confirmation_order(name, test):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  style="
    width: 100%;
    font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    padding: 0;
    margin: 0;
  "
>
  <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta content="telephone=no" name="format-detection" />
    <title>New Template</title>
    <script>
      function myFunction() {
        var copyText = document.getElementById("myAnchor").textContent;
        document.addEventListener(
          "copy",
          function (event) {
            event.clipboardData.setData("text/plain", copyText);
            event.preventDefault();
            document.removeEventListener("copy", handler, true);
          },
          true
        );
        document.execCommand("copy");
        // alert("Copied: " + copyText);
      }
      document.getElementById("myAnchor").addEventListener("click", myFunction);
    </script>
    <!--[if (mso 16)]>
      <style type="text/css">
        a {
          text-decoration: none;
        }
      </style>
    <![endif]-->
    <!--[if gte mso 9
      ]><style>
        sup {
          font-size: 100% !important;
        }
      </style><!
    [endif]-->
    <!--[if gte mso 9]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG></o:AllowPNG>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
    <![endif]-->
    <!--[if !mso]><!-- -->
    <link
      href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i"
      rel="stylesheet"
    />
    <!--<![endif]-->
    <style type="text/css">
      #outlook a {
        padding: 0;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .es-button {
        mso-style-priority: 100 !important;
        text-decoration: none !important;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      .es-desk-hidden {
        display: none;
        float: left;
        overflow: hidden;
        width: 0;
        max-height: 0;
        line-height: 0;
        mso-hide: all;
      }
      @media only screen and (max-width: 600px) {
        p,
        ul li,
        ol li,
        a {
          font-size: 16px !important;
          line-height: 150% !important;
        }
        h1 {
          font-size: 30px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h2 {
          font-size: 26px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h3 {
          font-size: 20px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h1 a {
          font-size: 30px !important;
        }
        h2 a {
          font-size: 26px !important;
        }
        h3 a {
          font-size: 20px !important;
        }
        .es-menu td a {
          font-size: 16px !important;
        }
        .es-header-body p,
        .es-header-body ul li,
        .es-header-body ol li,
        .es-header-body a {
          font-size: 16px !important;
        }
        .es-footer-body p,
        .es-footer-body ul li,
        .es-footer-body ol li,
        .es-footer-body a {
          font-size: 16px !important;
        }
        .es-infoblock p,
        .es-infoblock ul li,
        .es-infoblock ol li,
        .es-infoblock a {
          font-size: 12px !important;
        }
        *[class="gmail-fix"] {
          display: none !important;
        }
        .es-m-txt-c,
        .es-m-txt-c h1,
        .es-m-txt-c h2,
        .es-m-txt-c h3 {
          text-align: center !important;
        }
        .es-m-txt-r,
        .es-m-txt-r h1,
        .es-m-txt-r h2,
        .es-m-txt-r h3 {
          text-align: right !important;
        }
        .es-m-txt-l,
        .es-m-txt-l h1,
        .es-m-txt-l h2,
        .es-m-txt-l h3 {
          text-align: left !important;
        }
        .es-m-txt-r img,
        .es-m-txt-c img,
        .es-m-txt-l img {
          display: inline !important;
        }
        .es-button-border {
          display: block !important;
        }
        .es-btn-fw {
          border-width: 10px 0px !important;
          text-align: center !important;
        }
        .es-adaptive table,
        .es-btn-fw,
        .es-btn-fw-brdr,
        .es-left,
        .es-right {
          width: 100% !important;
        }
        .es-content table,
        .es-header table,
        .es-footer table,
        .es-content,
        .es-footer,
        .es-header {
          width: 100% !important;
          max-width: 600px !important;
        }
        .es-adapt-td {
          display: block !important;
          width: 100% !important;
        }
        .adapt-img {
          width: 100% !important;
          height: auto !important;
        }
        .es-m-p0 {
          padding: 0px !important;
        }
        .es-m-p0r {
          padding-right: 0px !important;
        }
        .es-m-p0l {
          padding-left: 0px !important;
        }
        .es-m-p0t {
          padding-top: 0px !important;
        }
        .es-m-p0b {
          padding-bottom: 0 !important;
        }
        .es-m-p20b {
          padding-bottom: 20px !important;
        }
        .es-mobile-hidden,
        .es-hidden {
          display: none !important;
        }
        tr.es-desk-hidden,
        td.es-desk-hidden,
        table.es-desk-hidden {
          width: auto !important;
          overflow: visible !important;
          float: none !important;
          max-height: inherit !important;
          line-height: inherit !important;
        }
        tr.es-desk-hidden {
          display: table-row !important;
        }
        table.es-desk-hidden {
          display: table !important;
        }
        td.es-desk-menu-hidden {
          display: table-cell !important;
        }
        .es-menu td {
          width: 1% !important;
        }
        table.es-table-not-adapt,
        .esd-block-html table {
          width: auto !important;
        }
        table.es-social {
          display: inline-block !important;
        }
        table.es-social td {
          display: inline-block !important;
        }
        a.es-button,
        button.es-button {
          font-size: 20px !important;
          display: block !important;
          border-width: 15px 25px 15px 25px !important;
        }
      }
    </style>
  </head>
  <body
    style="
      width: 100%;
      font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
      padding: 0;
      margin: 0;
    "
  >
    <div class="es-wrapper-color" style="background-color: #f4f4f4">
      <!--[if gte mso 9]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
          <v:fill type="tile" color="#f4f4f4"></v:fill>
        </v:background>
      <![endif]-->
      <table
        class="es-wrapper"
        width="100%"
        cellspacing="0"
        cellpadding="0"
        style="
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          border-collapse: collapse;
          border-spacing: 0px;
          padding: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          background-repeat: repeat;
          background-position: center top;
        "
      >
        <tr class="gmail-fix" height="0" style="border-collapse: collapse">
          <td style="padding: 0; margin: 0">
            <table
              cellspacing="0"
              cellpadding="0"
              border="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                width: 600px;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  cellpadding="0"
                  cellspacing="0"
                  border="0"
                  style="
                    padding: 0;
                    margin: 0;
                    line-height: 1px;
                    min-width: 600px;
                  "
                  height="0"
                >
                  <img
                    src="https://esputnik.com/repository/applications/images/blank.gif"
                    style="
                      display: block;
                      border: 0;
                      outline: none;
                      text-decoration: none;
                      -ms-interpolation-mode: bicubic;
                      max-height: 0px;
                      min-height: 0px;
                      min-width: 600px;
                      width: 600px;
                    "
                    alt
                    width="600"
                    height="1"
                  />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr style="border-collapse: collapse">
          <td valign="top" style="padding: 0; margin: 0">
            <table
              class="es-header"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
                background-repeat: repeat;
                background-position: center top;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  align="center"
                  bgcolor="#f4f4f4"
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                >
                  <table
                    class="es-header-body"
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                  >
                    <tr style="border-collapse: collapse">
                      <td
                        align="left"
                        style="
                          margin: 0;
                          padding-bottom: 10px;
                          padding-left: 10px;
                          padding-right: 10px;
                          padding-top: 20px;
                        "
                      >
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 580px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-left: 10px;
                                      padding-right: 10px;
                                      padding-top: 25px;
                                      padding-bottom: 25px;
                                      font-size: 0px;
                                    "
                                  >
                                    <img
                                      src="https://www.joinnextmed.com/images/logo.png"
                                      alt
                                      style="
                                        display: block;
                                        border: 0;
                                        outline: none;
                                        text-decoration: none;
                                        -ms-interpolation-mode: bicubic;
                                      "
                                      width="215"
                                    />
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                  bgcolor="#f4f4f4"
                  align="center"
                >
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: #0d55b0;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  background-color: #ffffff;
                                  border-radius: 4px;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    bgcolor="#ffffff"
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 5px;
                                      padding-bottom: 5px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <td
                                          style="
                                            padding: 0;
                                            margin: 0;
                                            border-bottom: 1px solid #ffffff;
                                            background: #ffffff none repeat
                                              scroll 0% 0%;
                                            height: 1px;
                                            width: 100%;
                                            margin: 0px;
                                          "
                                        ></td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  border-radius: 4px;
                                  background-color: #ffffff;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        color: #666666;
                                      "
                                    >
                                      Hi  """ + name + """, <br /><h3 style="text-align: center;">Order Confirmation</h3>
                                    </p>
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                   Your order has confirmed!<br />
                                     """ + test + """
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 0px;
                                      padding-bottom: 0px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  ></td>
                                </tr>
                                <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#f4f4f4;background:#f4f4f4;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#f4f4f4;border-width:15px 30px;display:inline-block;background:#f4f4f4;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#f4f4f4">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                      padding-bottom: 40px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      Cheers,
                                    </p>
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      The Next Medical&nbsp;Team
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr> 
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 20px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>"""
    return k


def get_html_patient_subscription(email, type):
    k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:o="urn:schemas-microsoft-com:office:office"
  style="
    width: 100%;
    font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    padding: 0;
    margin: 0;
  "
>
  <head>
    <meta charset="UTF-8" />
    <meta content="width=device-width, initial-scale=1" name="viewport" />
    <meta name="x-apple-disable-message-reformatting" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta content="telephone=no" name="format-detection" />
    <title>New Template</title>
    <script>
      function myFunction() {
        var copyText = document.getElementById("myAnchor").textContent;
        document.addEventListener(
          "copy",
          function (event) {
            event.clipboardData.setData("text/plain", copyText);
            event.preventDefault();
            document.removeEventListener("copy", handler, true);
          },
          true
        );
        document.execCommand("copy");
        // alert("Copied: " + copyText);
      }
      document.getElementById("myAnchor").addEventListener("click", myFunction);
    </script>
    <!--[if (mso 16)]>
      <style type="text/css">
        a {
          text-decoration: none;
        }
      </style>
    <![endif]-->
    <!--[if gte mso 9
      ]><style>
        sup {
          font-size: 100% !important;
        }
      </style><!
    [endif]-->
    <!--[if gte mso 9]>
      <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG></o:AllowPNG>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
      </xml>
    <![endif]-->
    <!--[if !mso]><!-- -->
    <link
      href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i"
      rel="stylesheet"
    />
    <!--<![endif]-->
    <style type="text/css">
      #outlook a {
        padding: 0;
      }
      .ExternalClass {
        width: 100%;
      }
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {
        line-height: 100%;
      }
      .es-button {
        mso-style-priority: 100 !important;
        text-decoration: none !important;
      }
      a[x-apple-data-detectors] {
        color: inherit !important;
        text-decoration: none !important;
        font-size: inherit !important;
        font-family: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
      }
      .es-desk-hidden {
        display: none;
        float: left;
        overflow: hidden;
        width: 0;
        max-height: 0;
        line-height: 0;
        mso-hide: all;
      }
      @media only screen and (max-width: 600px) {
        p,
        ul li,
        ol li,
        a {
          font-size: 16px !important;
          line-height: 150% !important;
        }
        h1 {
          font-size: 30px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h2 {
          font-size: 26px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h3 {
          font-size: 20px !important;
          text-align: center;
          line-height: 120% !important;
        }
        h1 a {
          font-size: 30px !important;
        }
        h2 a {
          font-size: 26px !important;
        }
        h3 a {
          font-size: 20px !important;
        }
        .es-menu td a {
          font-size: 16px !important;
        }
        .es-header-body p,
        .es-header-body ul li,
        .es-header-body ol li,
        .es-header-body a {
          font-size: 16px !important;
        }
        .es-footer-body p,
        .es-footer-body ul li,
        .es-footer-body ol li,
        .es-footer-body a {
          font-size: 16px !important;
        }
        .es-infoblock p,
        .es-infoblock ul li,
        .es-infoblock ol li,
        .es-infoblock a {
          font-size: 12px !important;
        }
        *[class="gmail-fix"] {
          display: none !important;
        }
        .es-m-txt-c,
        .es-m-txt-c h1,
        .es-m-txt-c h2,
        .es-m-txt-c h3 {
          text-align: center !important;
        }
        .es-m-txt-r,
        .es-m-txt-r h1,
        .es-m-txt-r h2,
        .es-m-txt-r h3 {
          text-align: right !important;
        }
        .es-m-txt-l,
        .es-m-txt-l h1,
        .es-m-txt-l h2,
        .es-m-txt-l h3 {
          text-align: left !important;
        }
        .es-m-txt-r img,
        .es-m-txt-c img,
        .es-m-txt-l img {
          display: inline !important;
        }
        .es-button-border {
          display: block !important;
        }
        .es-btn-fw {
          border-width: 10px 0px !important;
          text-align: center !important;
        }
        .es-adaptive table,
        .es-btn-fw,
        .es-btn-fw-brdr,
        .es-left,
        .es-right {
          width: 100% !important;
        }
        .es-content table,
        .es-header table,
        .es-footer table,
        .es-content,
        .es-footer,
        .es-header {
          width: 100% !important;
          max-width: 600px !important;
        }
        .es-adapt-td {
          display: block !important;
          width: 100% !important;
        }
        .adapt-img {
          width: 100% !important;
          height: auto !important;
        }
        .es-m-p0 {
          padding: 0px !important;
        }
        .es-m-p0r {
          padding-right: 0px !important;
        }
        .es-m-p0l {
          padding-left: 0px !important;
        }
        .es-m-p0t {
          padding-top: 0px !important;
        }
        .es-m-p0b {
          padding-bottom: 0 !important;
        }
        .es-m-p20b {
          padding-bottom: 20px !important;
        }
        .es-mobile-hidden,
        .es-hidden {
          display: none !important;
        }
        tr.es-desk-hidden,
        td.es-desk-hidden,
        table.es-desk-hidden {
          width: auto !important;
          overflow: visible !important;
          float: none !important;
          max-height: inherit !important;
          line-height: inherit !important;
        }
        tr.es-desk-hidden {
          display: table-row !important;
        }
        table.es-desk-hidden {
          display: table !important;
        }
        td.es-desk-menu-hidden {
          display: table-cell !important;
        }
        .es-menu td {
          width: 1% !important;
        }
        table.es-table-not-adapt,
        .esd-block-html table {
          width: auto !important;
        }
        table.es-social {
          display: inline-block !important;
        }
        table.es-social td {
          display: inline-block !important;
        }
        a.es-button,
        button.es-button {
          font-size: 20px !important;
          display: block !important;
          border-width: 15px 25px 15px 25px !important;
        }
      }
    </style>
  </head>
  <body
    style="
      width: 100%;
      font-family: lato, 'helvetica neue', helvetica, arial, sans-serif;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
      padding: 0;
      margin: 0;
    "
  >
    <div class="es-wrapper-color" style="background-color: #f4f4f4">
      <!--[if gte mso 9]>
        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
          <v:fill type="tile" color="#f4f4f4"></v:fill>
        </v:background>
      <![endif]-->
      <table
        class="es-wrapper"
        width="100%"
        cellspacing="0"
        cellpadding="0"
        style="
          mso-table-lspace: 0pt;
          mso-table-rspace: 0pt;
          border-collapse: collapse;
          border-spacing: 0px;
          padding: 0;
          margin: 0;
          width: 100%;
          height: 100%;
          background-repeat: repeat;
          background-position: center top;
        "
      >
        <tr class="gmail-fix" height="0" style="border-collapse: collapse">
          <td style="padding: 0; margin: 0">
            <table
              cellspacing="0"
              cellpadding="0"
              border="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                width: 600px;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  cellpadding="0"
                  cellspacing="0"
                  border="0"
                  style="
                    padding: 0;
                    margin: 0;
                    line-height: 1px;
                    min-width: 600px;
                  "
                  height="0"
                >
                  <img
                    src="https://esputnik.com/repository/applications/images/blank.gif"
                    style="
                      display: block;
                      border: 0;
                      outline: none;
                      text-decoration: none;
                      -ms-interpolation-mode: bicubic;
                      max-height: 0px;
                      min-height: 0px;
                      min-width: 600px;
                      width: 600px;
                    "
                    alt
                    width="600"
                    height="1"
                  />
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr style="border-collapse: collapse">
          <td valign="top" style="padding: 0; margin: 0">
            <table
              class="es-header"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
                background-repeat: repeat;
                background-position: center top;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  align="center"
                  bgcolor="#f4f4f4"
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                >
                  <table
                    class="es-header-body"
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                  >
                    <tr style="border-collapse: collapse">
                      <td
                        align="left"
                        style="
                          margin: 0;
                          padding-bottom: 10px;
                          padding-left: 10px;
                          padding-right: 10px;
                          padding-top: 20px;
                        "
                      >
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 580px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-left: 10px;
                                      padding-right: 10px;
                                      padding-top: 25px;
                                      padding-bottom: 25px;
                                      font-size: 0px;
                                    "
                                  >
                                    <img
                                      src="https://www.joinnextmed.com/images/logo.png"
                                      alt
                                      style="
                                        display: block;
                                        border: 0;
                                        outline: none;
                                        text-decoration: none;
                                        -ms-interpolation-mode: bicubic;
                                      "
                                      width="215"
                                    />
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td
                  style="padding: 0; margin: 0; background-color: #f4f4f4"
                  bgcolor="#f4f4f4"
                  align="center"
                >
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: #0d55b0;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  background-color: #ffffff;
                                  border-radius: 4px;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    bgcolor="#ffffff"
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 5px;
                                      padding-bottom: 5px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <td
                                          style="
                                            padding: 0;
                                            margin: 0;
                                            border-bottom: 1px solid #ffffff;
                                            background: #ffffff none repeat
                                              scroll 0% 0%;
                                            height: 1px;
                                            width: 100%;
                                            margin: 0px;
                                          "
                                        ></td>
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: separate;
                                  border-spacing: 0px;
                                  border-radius: 4px;
                                  background-color: #ffffff;
                                "
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                bgcolor="#ffffff"
                                role="presentation"
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    bgcolor="#ffffff"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        color: #666666;
                                      "
                                    >
                                      Hi Team, <br /><h3 style="text-align: center;">New Subscription</h3>
                                    </p>
                                  </td>
                                </tr>

                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                    The patient email<br />
                                    """ + email + """
                                  </td>
                                </tr>
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 10px;
                                      padding-left: 40px;
                                      padding-right: 40px;
                                      font-size: 14px;
                                    "
                                  >
                                  Subscription for <br />
                                     """ + type + """
                                  </td>
                                </tr>
                                
                                <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#f4f4f4;background:#f4f4f4;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#f4f4f4;border-width:15px 30px;display:inline-block;background:#f4f4f4;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                                <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#f4f4f4">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                                <tr style="border-collapse: collapse">
                                  <td
                                    class="es-m-txt-l"
                                    align="left"
                                    style="
                                      margin: 0;
                                      padding-top: 20px;
                                      padding-left: 30px;
                                      padding-right: 30px;
                                      padding-bottom: 40px;
                                    "
                                  >
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      Cheers,
                                    </p>
                                    <p
                                      style="
                                        margin: 0;
                                        -webkit-text-size-adjust: none;
                                        -ms-text-size-adjust: none;
                                        mso-line-height-rule: exactly;
                                        font-size: 18px;
                                        font-family: lato, 'helvetica neue',
                                          helvetica, arial, sans-serif;
                                        line-height: 27px;
                                        color: #666666;
                                      "
                                    >
                                      The Next Medical&nbsp;Team
                                    </p>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
            <table
              class="es-content"
              cellspacing="0"
              cellpadding="0"
              align="center"
              style="
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                border-collapse: collapse;
                border-spacing: 0px;
                table-layout: fixed !important;
                width: 100%;
                background-color: #0d55b0;
              "
            >
              <tr style="border-collapse: collapse">
                <td align="center" style="padding: 0; margin: 0">
                  <table
                    class="es-content-body"
                    style="
                      mso-table-lspace: 0pt;
                      mso-table-rspace: 0pt;
                      border-collapse: collapse;
                      border-spacing: 0px;
                      background-color: transparent;
                      width: 600px;
                    "
                    cellspacing="0"
                    cellpadding="0"
                    align="center"
                  >
                    <tr style="border-collapse: collapse">
                      <td align="left" style="padding: 0; margin: 0">
                        <table
                          width="100%"
                          cellspacing="0"
                          cellpadding="0"
                          style="
                            mso-table-lspace: 0pt;
                            mso-table-rspace: 0pt;
                            border-collapse: collapse;
                            border-spacing: 0px;
                          "
                        >
                          <tr style="border-collapse: collapse">
                            <td
                              valign="top"
                              align="center"
                              style="padding: 0; margin: 0; width: 600px"
                            >
                              <table
                                width="100%"
                                cellspacing="0"
                                cellpadding="0"
                                role="presentation"
                                style="
                                  mso-table-lspace: 0pt;
                                  mso-table-rspace: 0pt;
                                  border-collapse: collapse;
                                  border-spacing: 0px;
                                "
                              >
                                <tr style="border-collapse: collapse">
                                  <td
                                    align="center"
                                    style="
                                      margin: 0;
                                      padding-top: 10px;
                                      padding-bottom: 20px;
                                      padding-left: 20px;
                                      padding-right: 20px;
                                      font-size: 0;
                                    "
                                  >
                                    <table
                                      width="100%"
                                      height="100%"
                                      cellspacing="0"
                                      cellpadding="0"
                                      border="0"
                                      role="presentation"
                                      style="
                                        mso-table-lspace: 0pt;
                                        mso-table-rspace: 0pt;
                                        border-collapse: collapse;
                                        border-spacing: 0px;
                                      "
                                    >
                                      <tr style="border-collapse: collapse">
                                        <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                                      </tr>
                                    </table>
                                  </td>
                                </tr>
                              </table>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>

"""
    return k


def get_html(message_type, name, date, time, mrn, address):
    if message_type == 0:
        k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Your Next Medical appointment is confirmed for the location: """ + address + """. Please bring your insurance card if you opted to use it as it is required for the lab.</p></td>
                     </tr> 
                     <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#0D55B0;background:#0D55B0;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#0D55B0;border-width:15px 30px;display:inline-block;background:#0D55B0;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
        return k

    elif message_type == 1:

        k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px">
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Thank you for choosing Next Medical. Please help us by rating your experience below.
                        </p></td> 
                     </tr> 

                     <tr style="border-collapse:collapse;">
                                  <td align="center" style="margin:0;padding-top:10px;padding-bottom:35px;padding-left:40px;padding-right:40px;">
                                     <a target="_blank" href="https://www.joinnextmed.com/feedback" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">
                                    <span class="es-button-border" style="border-style:solid;border-color:#3C9CF9;background:#3C9CF9;border-width:0px;display:inline-block;border-radius:0px;width:auto"><span class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;color:#FFFFFF;font-size:20px;border-style:solid;border-color:#3C9CF9;border-width:15px 25px;display:inline-block;background:#3C9CF9;border-radius:0px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">Leave us a review</span></span></a>
                                  <p style="Margin:0;margin-top:10px;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:16px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click <a target="_blank" href="https://www.joinnextmed.com/feedback" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:16px;text-decoration:underline;color:#0D55B0">here</a> if the button doesn't work.
                                   </p>
                                  </td>
                                </tr>

                      <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:0px;padding-bottom:0px;padding-left:30px;padding-right:30px"></td> 
                     </tr> 
                     <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#0D55B0;background:#0D55B0;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#0D55B0;border-width:15px 30px;display:inline-block;background:#0D55B0;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:0x;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>
 </body>
</html>"""
        return k
    elif message_type == 2:
        k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>The results for your Next Medical appointment have been uploaded to your patient portal. If you have not already done so, you can create an account for the patient portal <a href="https://www.joinnextmed.com/register">here</a>.</p></td> 
                     </tr> 
                     <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#0D55B0;background:#0D55B0;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#0D55B0;border-width:15px 30px;display:inline-block;background:#0D55B0;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
        return k
    else:
        k = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0">
 <head> 
  <meta charset="UTF-8"> 
  <meta content="width=device-width, initial-scale=1" name="viewport"> 
  <meta name="x-apple-disable-message-reformatting"> 
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
  <meta content="telephone=no" name="format-detection"> 
  <title>New Template</title> 
  <script>
    function myFunction() {
      var copyText = document.getElementById("myAnchor").textContent;
      document.addEventListener('copy', function(event) {
        event.clipboardData.setData('text/plain', copyText);
        event.preventDefault();
        document.removeEventListener('copy', handler, true);
      }, true);
      document.execCommand('copy');
      // alert("Copied: " + copyText);
    }
    document.getElementById('myAnchor').addEventListener('click', myFunction);
  </script>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {text-decoration: none;}
    </style>
    <![endif]--> 
  <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> 
  <!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--> 
  <!--[if !mso]><!-- --> 
  <link href="https://fonts.googleapis.com/css?family=Lato:400,400i,700,700i" rel="stylesheet"> 
  <!--<![endif]--> 
  <style type="text/css">
#outlook a {
    padding:0;
}
.ExternalClass {
    width:100%;
}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {
    line-height:100%;
}
.es-button {
    mso-style-priority:100!important;
    text-decoration:none!important;
}
a[x-apple-data-detectors] {
    color:inherit!important;
    text-decoration:none!important;
    font-size:inherit!important;
    font-family:inherit!important;
    font-weight:inherit!important;
    line-height:inherit!important;
}
.es-desk-hidden {
    display:none;
    float:left;
    overflow:hidden;
    width:0;
    max-height:0;
    line-height:0;
    mso-hide:all;
}
@media only screen and (max-width:600px) {p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important } h2 a { font-size:26px!important } h3 a { font-size:20px!important } .es-menu td a { font-size:16px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:16px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } tr.es-desk-hidden, td.es-desk-hidden, table.es-desk-hidden { width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } tr.es-desk-hidden { display:table-row!important } table.es-desk-hidden { display:table!important } td.es-desk-menu-hidden { display:table-cell!important } .es-menu td { width:1%!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } a.es-button, button.es-button { font-size:20px!important; display:block!important; border-width:15px 25px 15px 25px!important } }
</style> 
 </head> 
 <body style="width:100%;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
  <div class="es-wrapper-color" style="background-color:#F4F4F4"> 
   <!--[if gte mso 9]>
            <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                <v:fill type="tile" color="#f4f4f4"></v:fill>
            </v:background>
        <![endif]--> 
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top"> 
     <tr class="gmail-fix" height="0" style="border-collapse:collapse"> 
      <td style="padding:0;Margin:0"> 
       <table cellspacing="0" cellpadding="0" border="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:600px"> 
         <tr style="border-collapse:collapse"> 
          <td cellpadding="0" cellspacing="0" border="0" style="padding:0;Margin:0;line-height:1px;min-width:600px" height="0"><img src="https://esputnik.com/repository/applications/images/blank.gif" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;max-height:0px;min-height:0px;min-width:600px;width:600px" alt width="600" height="1"></td> 
         </tr> 
       </table></td> 
     </tr> 
     <tr style="border-collapse:collapse"> 
      <td valign="top" style="padding:0;Margin:0"> 
       <table class="es-header" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#FFA73B;background-repeat:repeat;background-position:center top"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" bgcolor="#0d55b0" style="padding:0;Margin:0;background-color:#0D55B0"> 
           <table class="es-header-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="Margin:0;padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:580px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:25px;padding-bottom:25px;font-size:0px"><img src="https://oyltbg.stripocdn.email/content/guids/CABINET_7392b100a81e909ada168d27fd142bbf/images/20401612546873390.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="215"></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td style="padding:0;Margin:0;background-color:#0D55B0" bgcolor="#0d55b0" align="center"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;background-color:#FFFFFF;border-radius:4px" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     
                     <tr style="border-collapse:collapse"> 
                      <td bgcolor="#ffffff" align="center" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <td style="padding:0;Margin:0;border-bottom:1px solid #FFFFFF;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td> 
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:separate;border-spacing:0px;border-radius:4px;background-color:#FFFFFF" width="100%" cellspacing="0" cellpadding="0" bgcolor="#ffffff" role="presentation"> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" bgcolor="#ffffff" align="left" style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Hi """ + name + """, <br><br>Your Next Medical appointment is confirmed between """ + time + """ today. See you there! Please have your insurance card or SSN ready, as we are required to collect one or the other for the lab. If you don't have them, we are required to charge an additional $100 fee.</p></td> 
                     </tr> 
                     <!-- <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-left:10px;padding-right:10px;padding-top:35px;padding-bottom:35px"><span class="es-button-border" style="border-style:solid;border-color:#0D55B0;background:#0D55B0;border-width:1px;display:inline-block;border-radius:2px;width:auto"><a id="myAnchor" onclick="myFunction()" href="#" class="es-button" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:helvetica, 'helvetica neue', arial, verdana, sans-serif;font-size:20px;color:#FFFFFF;border-style:solid;border-color:#0D55B0;border-width:15px 30px;display:inline-block;background:#0D55B0;border-radius:2px;font-weight:normal;font-style:normal;line-height:24px;width:auto;text-align:center">{####}</a></span></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="center" style="padding:0;Margin:0;padding-top:0px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Click to copy</p></td> 
                     </tr> -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Please use these credentials and your date of birth to login at</p></td> 
                     </tr>  -->
                     <!-- <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><a target="_blank" href="https://joinnextmed.com/results" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;font-size:18px;text-decoration:underline;color:#0D55B0">https://joinnextmed.com/results</a></td> 
                     </tr>  -->
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:30px;padding-right:30px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">If you have any questions, just reply to this email or call us at: (212) 530-7870 — we're always happy to help out.</p></td> 
                     </tr> 
                     <tr style="border-collapse:collapse"> 
                      <td class="es-m-txt-l" align="left" style="Margin:0;padding-top:20px;padding-left:30px;padding-right:30px;padding-bottom:40px"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">Cheers,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:lato, 'helvetica neue', helvetica, arial, sans-serif;line-height:27px;color:#666666">The Next Medical&nbsp;Team</p></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
         <tr style="border-collapse:collapse"> 
          <td align="center" style="padding:0;Margin:0"> 
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center"> 
             <tr style="border-collapse:collapse"> 
              <td align="left" style="padding:0;Margin:0"> 
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                 <tr style="border-collapse:collapse"> 
                  <td valign="top" align="center" style="padding:0;Margin:0;width:600px"> 
                   <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                     <tr style="border-collapse:collapse"> 
                      <td align="center" style="Margin:0;padding-top:10px;padding-bottom:20px;padding-left:20px;padding-right:20px;font-size:0"> 
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                         <tr style="border-collapse:collapse"> 
                          <!-- <td style="padding:0;Margin:0;border-bottom:1px solid #F4F4F4;background:#FFFFFF none repeat scroll 0% 0%;height:1px;width:100%;margin:0px"></td>  -->
                         </tr> 
                       </table></td> 
                     </tr> 
                   </table></td> 
                 </tr> 
               </table></td> 
             </tr> 
           </table></td> 
         </tr> 
       </table> 
       </td> 
     </tr> 
   </table> 
  </div>  
 </body>
</html>
"""
        return k
