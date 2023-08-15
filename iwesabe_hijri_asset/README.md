Example Code
Xml:

    For Picker :

        <label for="iqama_issue_date_hijri" string="Issue Date (Hijri)"/>
        <div class="o_row">
            <field name="iqama_issue_date_hijri"/>
            <button context="{'date_field': 'iqama_issue_date_hijri'}" name="%(iwesabe_hijri_asset.call_field_edit)d" type="action"  string=" " icon="fa-calendar" class="oe_edit_only"/>
        </div>


    For Conversion :

    <button context="{'field_to':'iqama_issue_date','field_from':'iqama_issue_date_hijri'}" name="hijri2Gregorian" type="object"  string=" " icon="fa-refresh" class="oe_edit_only" help="Conversion with hijri; There is a small probability of one day error"/>

