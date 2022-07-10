Feature: As a developper, I want a browser open with a session

  @dev
  Scenario: start an initialized session and wait
    Given user on the admin page
    When I click on the "Create my first page" link
    And I click on the "blog:HomePage" link
    And I fill the field "slug" with "home"
    And I fill the field "title" with "welcome home"
    And I fill the field "description" with "there is not place like home"
    # First paragraph
    And I click on the "Add Item" button
    And I fill the "second" field "title" with "Intro"
    And I fill the textarea field "body" with "<p>Welcome aboard!</p>"
    # Second paragraph
    And I click on the "Add Item" button
    And I fill the "third" field "title" with "Outro"
    And I fill the "second" textarea field "body" with "<p>Rich text widget not implemented yet</p>"
    And I click on the "Submit" button
    And I wait
