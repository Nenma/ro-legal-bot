from enum import StrEnum


class LawUrls(StrEnum):
    ADMINISTRATIVE = "https://legislatie.just.ro/Public/FormaPrintabila/00000G26T9IKD8IXCIZ0X39N88WZQ5GJ"
    CIVIL = "https://legislatie.just.ro/Public/FormaPrintabila/00000G1TT7EZVJJX6870CWN6ZG1TWPAC"
    CIVIL_PROCEDURE = "https://legislatie.just.ro/Public/FormaPrintabila/00000G1NE6WQB9B6WYG13YGXTQETNYA8"
    CONSTITUTION = "https://legislatie.just.ro/Public/FormaPrintabila/00000G0NF8LQJNGG75M2SUMLP2PIT6ZP"
    FISCAL = "https://legislatie.just.ro/Public/FormaPrintabila/00000G1ZAKIDCF325CT2OM2WBUU98MOP"
    FISCAL_PROCEDURE = "https://legislatie.just.ro/Public/FormaPrintabila/00000G1SA6VV3H1PY8920ESSHWCB3WXT"
    LABOR = "https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCE89TJASJDO1SWLGVM5I6DWB"
    PENAL = "https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCJVMCPZK1D5301YV9BG07ZE3"
    PENAL_PROCEDURE = "https://legislatie.just.ro/Public/FormaPrintabila/00000G3SGIENTQKF6QX0SUWA2W5Y3ZV3"

    @classmethod
    def list(cls):
        return list(map(lambda elem: elem.value, cls))