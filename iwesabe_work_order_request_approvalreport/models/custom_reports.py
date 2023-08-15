from odoo import api, models

class CustomAbstract(models.AbstractModel):
    _name = 'custom.abstract'
    _description = '''
        This abstract model consists of general methods
        need for the custom reports.
    '''

    @api.model
    def display_partner_details(self, partner_id):
        """
            This method simply returns qweb displayable partner details.
        """
        partner_address = []
        partner_address.append(partner_id.name)
        if partner_id.street:
            partner_address.append(partner_id.street)
        
        street_city_zip = ""
        if partner_id.street2:
            street_city_zip += partner_id.street2
            street_city_zip += ", "
        if partner_id.city:
            street_city_zip += partner_id.city
            street_city_zip += ", "
        if partner_id.zip:
            street_city_zip += partner_id.zip
        if street_city_zip:
            partner_address.append(street_city_zip)

        state_country = ""
        if partner_id.state_id:
            state_country += partner_id.state_id.name
            state_country += ", "
        if partner_id.country_id:
            state_country += partner_id.country_id.name
        if state_country:
            partner_address.append(state_country)

        tel_mobile = "Tel/Mobile: "
        if partner_id.mobile:
            tel_mobile += partner_id.mobile + ", "
        if partner_id.phone:
            tel_mobile += partner_id.phone
        partner_address.append(tel_mobile)

        return partner_address
        
        
        
