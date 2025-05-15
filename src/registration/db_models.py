from tortoise import Model, fields


class RedirectURIs(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='redirect_uris', pk=True)
    uri = fields.CharField(max_length=2083)


class ClientGrantTypes(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='grant_types', pk=True)
    grant_type = fields.CharField(max_length=43, unique=True)


class ClientResponseTypes(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='response_types', pk=True)
    response_type = fields.CharField(max_length=43, unique=True)


class ClientScopes(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='scopes', pk=True)
    scope = fields.CharField(max_length=256, unique=True)


class ClientContacts(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='contacts', pk=True)
    contact = fields.CharField(max_length=256, unique=True)


class ClientJWKs(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='jwks', pk=True)
    jwk = fields.CharField(max_length=65536)


class ClientCredentials(Model):
    client: fields.ForeignKeyRelation["ClientMeta"] = fields.ForeignKeyField('core.ClientMeta',
                                                                             related_name='credentials', pk=True)
    client_secret = fields.CharField(max_length=256)
    client_id_issued_at = fields.IntField()
    client_secret_expires_at = fields.IntField(default=0)


class ClientMeta(Model):
    id = fields.UUIDField(pk=True)
    token_endpoint_auth_method = fields.CharField(max_length=19)
    client_name = fields.CharField(max_length=1024, null=True)
    client_uri = fields.CharField(max_length=2083, null=True)
    logo_uri = fields.CharField(max_length=2083, null=True)
    tos_uri = fields.CharField(max_length=2083, null=True)
    policy_uri = fields.CharField(max_length=2083, null=True)
    jwks_uri = fields.CharField(max_length=2083, null=True)
    software_id = fields.UUIDField(null=True)
    software_version = fields.CharField(max_length=512, null=True)

    grant_types: fields.ReverseRelation["ClientGrantTypes"]
    response_types: fields.ReverseRelation["ClientResponseTypes"]
    scopes: fields.ReverseRelation["ClientScopes"]
    contacts: fields.ReverseRelation["ClientContacts"]
    jwks: fields.ReverseRelation["ClientJWKs"]
    credentials: fields.ReverseRelation["ClientCredentials"]
    redirect_uris: fields.ReverseRelation["RedirectURIs"]

    async def full(self):
        await self.fetch_related("grant_types", "response_types", "scopes", "contacts", "jwks", "credentials",
                                 "redirect_uris")
        creds = await self.credentials.all().first()
        return {
            'id': self.id,
            'token_endpoint_auth_method': self.token_endpoint_auth_method,
            'client_name': self.client_name,
            'client_uri': self.client_uri,
            'logo_uri': self.logo_uri,
            'tos_uri': self.tos_uri,
            'policy_uri': self.policy_uri,
            'jwks_uri': self.jwks_uri,
            'software_id': self.software_id,
            'software_version': self.software_id,
            'grant_types': [grant_type.grant_type for grant_type in self.grant_types],
            'response_types': [response_type.response_type for response_type in self.response_types],
            'scopes': ' '.join([scope.scope for scope in self.scopes]),
            'contacts': [contact.contact for contact in self.contacts],
            'jwks': [jwk.jwk for jwk in self.jwks],
            'redirect_uris': [uri.uri for uri in self.redirect_uris],
            'client_secret_expires_at': creds.client_secret_expires_at,
            'client_id_issued_at': creds.client_id_issued_at
        }

    class Meta:
        unique_together = ('software_id', 'software_version')
