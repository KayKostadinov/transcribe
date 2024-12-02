from constructor import Constructor

constructor = Constructor(
    name='Transcribe',  # Your application name
    version='1.0',  # Your application version
    description='Audio transcription application',  # A short description
    author='Kay Kostadinov',  # Your name
    author_email='kay.kostadinov@gmail.com',  # Your email
    # url='your_website.com',  # Optional: Your website
    license='MIT',  # Or your license
    entry_points={
        'console_scripts': [
            'transcribe=main_script:main'  # Replace with your actual script and function
        ]
    },
    include_package_data=True,  # Include data files (like your styles.qss)
    # packages=['your_package_name'],  # If you have your code in a package
    install_requires=[
        'PyQt6==6.7.1',  # Or your PyQt6 version
        'openai-whisper'
    ]
)

if __name__ == '__main__':
    constructor.run()
