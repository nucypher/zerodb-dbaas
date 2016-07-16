$(document).ready(function() {
    $("#registration-form").submit(function() {
        var password = $("#inputPassword").val();
        scrypt(password, 'salt', 14, 8, 32, 5000, function(out) {
            var curve = sjcl.ecc.curves['k256']; // secp256k1
            var priv = sjcl.bn.fromBits(
                sjcl.codec.bytes.toBits(out));
            var raw_pub = curve.G.mult(priv);
            var pub = new sjcl.ecc.ecdsa.publicKey(curve, raw_pub)
                .serialize()
                .point;
            $("#inputPublicKey").val(pub);
            alert($("#inputPublicKey").val());
        });
        return false;
    });
});
