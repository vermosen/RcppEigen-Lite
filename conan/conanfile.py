import os, sys
from conans import ConanFile, tools, CMake

class RcppUtilsConan(ConanFile):
    name = "RcppUtils"
    settings = "os", "compiler", "build_type", "arch"
    description = "RcppUtils lib"
    url = "None"
    license = "None"
    author = "vermosen@yahoo.com"
    topics = None
    generators = 'cmake'
    cmake_files = ['%sConfig.cmake' % name,
                   '%sConfigVersion.cmake' % name,
                   '%sTargets.cmake' % name,
                   '%sTargets-*.cmake' % name]

    def source(self):
        pass

    def configure(self):
        self.requires("eigen/3.3.7@%s/%s" % (self.user, self.channel))
        self.requires("rcpp/1.0.4@%s/%s"  % (self.user, self.channel))
        
    def configure_cmake(self):

        src = os.path.join(self.source_folder, self._source_subfolder)
        cmake = CMake(self, set_cmake_flags=True)

        self.output.info('source folder location %s' % src)

        if self.settings.compiler == 'gcc':
            if self.settings.compiler.version in ['8', '8.4']:
                cmake.definitions["CMAKE_PROFILE"] = 'gcc84'
            elif self.settings.compiler.version in ['9', '9.3']:
                cmake.definitions["CMAKE_PROFILE"] = 'gcc93'
            else:
                self.output.info('compiler %s %s not supported' % 
                  (self.settings.compiler, self.settings.compiler.version))
        else:
            exit(1)

        cmake.configure(source_folder=src)

        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):

        self.output.info('executing packaging in folder %s' % os.getcwd())
        self.output.info('build folder is: %s' % self.build_folder)
        self.copy("*.h"  , dst="include", src="../include")

        if self.settings.os == 'Linux':
            try:
                path = "%s/%sTargets.cmake" % (self.build_folder, self.name)

                with open(path) as f:
                    content = f.read()
                    self.output.info('read %sTargets.cmake content [size=%s]' % (self.name, len(content)))

                import re, glob
                m = re.search(r'set\(_IMPORT_PREFIX \"([^\"]+)\"\)', content)
                self.output.info('found prefix value: %s' % m.group(1))
                files = glob.glob('%s/*Targets*.cmake' % self.build_folder)

                for f in files:
                    self.output.info('replacing prefix path in %s' % f)
                    tools.replace_in_file(f, m.group(1),
                        '${CONAN_%s_ROOT}' % self.name.upper(), strict=False)

                # step 2: substitute LIB_PATH
                with open("%s/%sConfig.cmake" % (self.build_folder, self.name)) as f:
                    content = f.read()
                    self.output.info('read %sConfig.cmake content [size: %s]' % (self.name, len(content)))

                    rgx = r'set\s*\(%s_CONAN_LIBS_DIRS_HINT\s+\"*([^\"]+)\"*\s*\)' % self.name.upper()
                    self.output.info('looking for regex %s' % rgx)
                    m = re.search(rgx, content)

                    if m is not None:
                        self.output.info('found lib install location: %s' % m.group(1))
                    else:
                        self.output.error('failed to parse file content %s' % content)
                        raise
                
                    for f in files:
                        self.output.info('replacing lib install location in %s' % f)
                        tools.replace_in_file(f, m.group(1),
                            '${CONAN_%s_ROOT}/lib' % self.name.upper(), strict=False)

                # step 3: copy the cmake config files
                self.output.info('looking for modified files in %s ...' % os.getcwd())

                for f in self.cmake_files:
                    self.copy("%s" % f, src=self.build_folder, keep_path=False)

            except:
                # always fails on the second lookup
                self.output.info('failed to parse cmake install files: %s' % sys.exc_info()[0])

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs     = ['lib']
        self.cpp_info.lib         = tools.collect_libs(self)
