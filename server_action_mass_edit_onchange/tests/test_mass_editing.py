# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.server_action_mass_edit.tests.test_mass_editing import (
    TestMassEditing,
)


class TestMassEditingWithOnChange(TestMassEditing):
    @patch("odoo.addons.base.models.res_partner.Partner.onchange_email")
    def test_wizard_field_onchange(self, patched):
        server_action_partner = self.env["ir.actions.server"].create(
            {
                "name": "Mass Edit Partner",
                "state": "mass_edit",
                "model_id": self.env.ref("base.model_res_partner").id,
            }
        )
        self.env["ir.actions.server.mass.edit.line"].create(
            [
                {
                    "server_action_id": server_action_partner.id,
                    "field_id": self.env.ref("base.field_res_partner__country_id").id,
                    "apply_onchanges": True,
                },
                {
                    "server_action_id": server_action_partner.id,
                    "field_id": self.env.ref("base.field_res_partner__email").id,
                    "apply_onchanges": False,
                },
            ]
        )
        self.assertEqual(
            server_action_partner.mass_edit_play_onchanges,
            {
                "country_id": True,
                "email": False,
            },
        )
        us_country = self.env.ref("base.us")
        mx_country = self.env.ref("base.mx")
        partners = self.env["res.partner"].create(
            [
                {
                    "name": "ACME",
                    "country_id": us_country.id,
                    "state_id": self.env.ref("base.state_us_1").id,
                },
                {
                    "name": "Example.com",
                    "country_id": us_country.id,
                    "state_id": self.env.ref("base.state_us_2").id,
                },
            ]
        )
        self.MassEditingWizard.with_context(
            server_action_id=server_action_partner.id,
            active_ids=partners.ids,
        ).create(
            {
                "selection__country_id": "set",
                "selection__email": "set",
                "country_id": mx_country,
                "email": "dummy@email.com",
            }
        )
        for partner in partners:
            self.assertEqual(partner.country_id, mx_country)
            # state_id is set to False by _onchange_country_id
            self.assertFalse(partner.state_id)
            self.assertEqual(partner.email, "dummy@email.com")
        # onchange_email is not called
        patched.assert_not_called()
