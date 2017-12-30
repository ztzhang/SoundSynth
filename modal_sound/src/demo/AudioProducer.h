#ifndef AUDIO_PRODUCER_INC
#   define AUDIO_PRODUCER_INC

#include <QSettings>
#include <QBuffer>
#include <QByteArray>
#include <QDir>
#include <QAudioOutput>
#include "sc/Vector3.hpp"
#include "geometry/Point3.hpp"
#include "modal/ModalModel.h"

#define NUM_THREADS 100

class FMMTransferEval;

class AudioProducer
{
    public:
        AudioProducer(const QSettings& settings, const QDir& dataDir);

        ~AudioProducer();

        void play(const Tuple3ui& tri, const Vector3d& dir, const Point3d& cam, float amplitude);
        void single_channel_synthesis(const Tuple3ui& tri, const Vector3d& dir, const Point3d& cam, float amplitude, int index_t=0);
//////////////////////////////////////////////////////////////////////////////
        void generate_continuous_wav(QByteArray& buffer, std::vector<double>& whole_soundBuffer);
        double TS;
        bool use_audio_device;
        std::vector<double> soundBuffer_[NUM_THREADS];
        QAudioFormat        format_;
//////////////////////////////////////////////////////////////////////////////

    private:
        void init();
        void enable_stereo(bool stereo);
        void load_vertex_map(const QString& filename);
        // synthesize sound just for single channel (no stereo sound)


        void load_moments(const QString& filename);

    private:
        double      short_component;
        double      short_period;
        double      long_period;

        bool        stereo_;

        // ------ for audio output ------
        QByteArray          buffer_;
        QBuffer             audioIO_;

        QAudioDeviceInfo*   device_;
        QAudioOutput*       audioOutput_;

        ModalModel*         modal_;

        int                 numFixed_;
        std::vector<double> mForce_[NUM_THREADS];        // force in modal space
        double              normalizeScale_;


        /* ------------ geometry ----------
         * map the vertex from surface triangle mesh to tet mesh
         * m_surfid[i] is the id in tet mesh of the i-th vertex in
         * surface triangle mesh
         */
        std::vector<int>    vidS2T_;        // vertex map for surface VID to tet VID
        std::vector<FMMTransferEval*> transfer_;
};

#endif
