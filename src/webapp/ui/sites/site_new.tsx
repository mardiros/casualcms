import React from "react";
import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormHelperText,
  FormLabel,
  Heading,
  Input,
} from "@chakra-ui/react";
import { PartialSite } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { useConfig } from "../../config";
import { useAuth } from "../login/hooks";
import { ApiErrorUI } from "../layout/error_api";
import { Navigate } from "react-router-dom";

export const SiteNew: React.FunctionComponent<{}> = () => {
  const auth = useAuth();
  const config = useConfig();
  const [createSucceed, setCreateSucceed] = React.useState<boolean>(false);
  const [error, setError] = React.useState<ApiError>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const hostname = formData.get("hostname") as string;
    const options = {
      root_page_path: formData.get("root_page_path") as string,
      default: formData.get("default") == "true",
      secure: formData.get("secure") == "true",
    };
    const siteResult = await config.api.site.createSite(
      auth.authenticatedUser?.token || "",
      hostname,
      options
    );

    siteResult
      .map(async (site: PartialSite) => {
        setCreateSucceed(true);
      })
      .mapErr((apiError) => {
        setError(apiError);
      });
  }

  if (createSucceed) {
    return <Navigate to="/admin/sites" replace />;
  }

  return (
    <Box maxW="720px">
      <Heading>New Site</Heading>
      {/* {<SiteBreadcrumb title="new page" />} */}
      <ApiErrorUI error={error} />
      <form onSubmit={handleSubmit}>
        <FormControl>
          <FormLabel>Hostname</FormLabel>
          <Input type="text" name="hostname" placeholder="hostname" />
          <FormHelperText>Hostname for this site.</FormHelperText>
        </FormControl>
        <FormControl>
          <FormLabel>Root Page</FormLabel>
          <Input type="text" name="root_page_path" placeholder="/index" />
          <FormHelperText>
            Path of the page, that will be the index page for this site (paged
            used for /).
          </FormHelperText>
        </FormControl>
        <FormControl>
          <Checkbox name="default" value="true">
            Default
          </Checkbox>
          <FormHelperText>
            If no site match, fallback to this one.
          </FormHelperText>
        </FormControl>
        <FormControl>
          <Checkbox>Secure</Checkbox>
          <FormHelperText>Use https.</FormHelperText>
        </FormControl>
        <FormControl paddingTop={5}>
          <Button type="submit">Submit</Button>
        </FormControl>
      </form>
    </Box>
  );
};
