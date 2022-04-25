public class Model {
    // a specific instantiation of a GAN model

    // latent spaces
    Latent @ latents[0];

    int id;

    // osc stuff
    "localhost" => string hostname;

    5005 => int sendPort;
    5006 => int recvPort;

    OscIn in;
    OscOut out;
    OscMsg msg;

    recvPort => in.port;
    out.dest(hostname, sendPort);

    fun Latent@ makeLatent() {

        in.addAddress("/make_latent/receive, i");
        out.start( "/make_latent/send" );
        out.send();

        <<< "waiting for response" >>>;
        in => now;

        int id;
        while(in.recv(msg)) {
            msg.getInt(0) => id;
            <<< "got left id", id >>>;
        }

        Latent l;
        id => l.id;
        latents << l;

        return l;
    }

    fun void face(Latent l) {
        out.start("/face");
        l.id => out.add;
        out.send();
    }

    fun void interpolate(Latent l, Latent left, Latent right, float scale) {
        out.start("/interpolate");
        l.id => out.add;
        left.id => out.add;
        right.id => out.add;
        scale => out.add;
        out.send();
    }
}