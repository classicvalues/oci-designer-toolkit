/*
** Copyright (c) 2020, 2021, Oracle and/or its affiliates.
** Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
*/
console.info('Loaded User Javascript');

/*
** Define User Class
*/
class User extends OkitArtifact {
    /*
    ** Create
    */
    constructor (data={}, okitjson={}) {
        super(okitjson);
        // Configure default values
        // const array_pos = okitjson.users ? okitjson.users.length + 1 : 0;
        // this.display_name = this.generateDefaultName(okitjson.users.length + 1);
        this.compartment_id = null;
        this.description = ''
        this.email = ''
        // Update with any passed data
        this.merge(data);
        this.convert();
    }
    /*
    ** Clone Functionality
    */
    clone() {
        return new User(JSON.clone(this), this.getOkitJson());
    }
    /*
    ** Name Generation
    */
    getNamePrefix() {
        return super.getNamePrefix() + 'usr';
    }
    /*
    ** Static Functionality
    */
    static getArtifactReference() {
        return 'User';
    }
}
/*
** Dynamically Add Model Functions
*/
OkitJson.prototype.newUser = function(data) {
    this.getUsers().push(new User(data, this));
    return this.getUsers()[this.getUsers().length - 1];
}
OkitJson.prototype.getUsers = function() {
    if (!this.users) {
        this.users = [];
    }
    return this.users;
}
OkitJson.prototype.getUser = function(id='') {
    for (let artefact of this.getUsers()) {
        if (artefact.id === id) {
            return artefact;
        }
    }
return undefined;
}
OkitJson.prototype.deleteUser = function(id) {
    this.users = this.users ? this.users.filter((u) => u.id !== id) : []
}

