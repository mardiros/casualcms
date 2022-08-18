import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { SnippetType } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SnippetBreadcrumb } from "../layout/breadcrumb";

const Form = withTheme(ChakraUITheme);

export const SnippetNew: React.FunctionComponent<{}> = () => {
  let { snippet_type } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [template, setTemplate] = React.useState<SnippetType | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadTemplate() {
      const template = await config.api.snippet_type.showSnippetType(
        token,
        snippet_type || ""
      );
      template
        .map((tpl: SnippetType) => setTemplate(tpl))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTemplate();
    return () => {
      setIsLoading(true);
      setError(null);
      setTemplate(null);
    };
  }, [snippet_type]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const snippet = data.formData;
    await config.api.snippet.createSnippet(token, snippet_type || "", snippet);
    navigate("/admin/snippets", { replace: true });
  };

  const data = {};
  return (
    <Box maxW="720px">
      <Heading>New Snippet</Heading>
      <SnippetBreadcrumb title="new snippet" />
      <ApiErrorUI error={error} />
      {template && (
        <Form
          schema={template.schema}
          uiSchema={template.uiSchema}
          formData={data}
          // onChange={() => console.log("changed")}
          onSubmit={onsubmit}
          // onError={() => console.log("errors")}
        />
      )}
    </Box>
  );
};
