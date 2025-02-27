/*
** Copyright (c) 2020, 2021, Oracle and/or its affiliates.
** Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
*/
console.info('Loaded Db Node Javascript');

/*
** Define Db Node Class
*/
class DbNode extends OkitArtifact {
    /*
    ** Create
    */
    constructor (data={}, okitjson={}) {
        super(okitjson);
        // Configure default values
        // this.display_name = this.generateDefaultName(okitjson.db_nodes.length + 1);
        this.compartment_id = data.parent_id;
        this.read_only = true;
        /*
        ** TODO: Add Resource / Artefact specific parameters and default
        */
        // Update with any passed data
        this.merge(data);
        this.convert();
        // TODO: If the Resource is within a Subnet but the subnet_iss is not at the top level then raise it with the following functions if not required delete them.
        // Expose subnet_id at the top level
        Object.defineProperty(this, 'subnet_id', {get: function() {return this.primary_mount_target.subnet_id;}, set: function(id) {this.primary_mount_target.subnet_id = id;}, enumerable: false });
        if (this.hostname) this.display_name = this.hostname
    }
    /*
    ** Clone Functionality
    */
    clone() {
        return new DbNode(JSON.clone(this), this.getOkitJson());
    }
    /*
    ** Name Generation
    */
    getNamePrefix() {
        return super.getNamePrefix() + 'dn';
    }
    /*
    ** Static Functionality
    */
    static getArtifactReference() {
        return 'Db Node';
    }
}
/*
** Dynamically Add Model Functions
*/
OkitJson.prototype.newDbNode = function(data) {
    this.getDbNodes().push(new DbNode(data, this));
    return this.getDbNodes()[this.getDbNodes().length - 1];
}
OkitJson.prototype.getDbNodes = function() {
    if (!this.db_nodes) {
        this.db_nodes = [];
    }
    return this.db_nodes;
}
OkitJson.prototype.getDbNode = function(id='') {
    for (let artefact of this.getDbNodes()) {
        if (artefact.id === id) {
            return artefact;
        }
    }
return undefined;
}
OkitJson.prototype.deleteDbNode = function(id) {
    this.db_nodes = this.db_nodes ? this.db_nodes.filter((r) => r.id !== id) : []
}

